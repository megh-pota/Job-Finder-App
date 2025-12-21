from flask import Blueprint, render_template, session, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Application
from app.routes.auth import login_required
import os
import uuid

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

# ============================
# CONFIG
# ============================
UPLOAD_FOLDER = "app/static/uploads/profile_pics"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================
# PROFILE COMPLETION SCORE
# (FEATURE D)
# ============================
def calculate_profile_score(user):
    score = 0

    if user.name:
        score += 20

    if user.profile_image:
        score += 20

    applications = Application.query.filter_by(seeker_user_id=user.id).all()
    if applications:
        score += 30

        latest_app = applications[-1]
        if latest_app.skills:
            score += 30

    return score


# ============================
# VIEW PROFILE
# ============================
@profile_bp.route("/")
@login_required
def my_profile():
    user = User.query.get(session.get("user_id"))

    profile_score = calculate_profile_score(user)

    return render_template(
        "profile.html",
        user=user,
        profile_score=profile_score
    )


# ============================
# CHANGE PASSWORD
# ============================
@profile_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    user = User.query.get(session.get("user_id"))

    if request.method == "POST":
        old_password = request.form.get("old")
        new_password = request.form.get("new")

        if not user.check_password(old_password):
            flash("Old password is incorrect.", "danger")
            return redirect(request.url)

        user.set_password(new_password)
        db.session.commit()

        flash("Password updated successfully!", "success")
        return redirect(url_for("profile.my_profile"))

    return render_template("profile_password.html")


# ============================
# EDIT PROFILE
# ============================
@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = User.query.get(session.get("user_id"))

    if request.method == "POST":
        user.name = request.form.get("name")
        user.email = request.form.get("email")

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.my_profile"))

    return render_template("profile_edit.html", user=user)


# ============================
# UPLOAD PROFILE PHOTO
# ============================
@profile_bp.route("/upload-photo", methods=["POST"])
@login_required
def upload_photo():
    user = User.query.get(session.get("user_id"))

    if "photo" not in request.files:
        flash("No file selected.", "danger")
        return redirect(url_for("profile.my_profile"))

    photo = request.files["photo"]

    if photo.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("profile.my_profile"))

    if not allowed_file(photo.filename):
        flash("Only JPG, PNG images allowed.", "danger")
        return redirect(url_for("profile.my_profile"))

    # File size check
    photo.seek(0, os.SEEK_END)
    size = photo.tell()
    photo.seek(0)

    if size > MAX_FILE_SIZE:
        flash("Image must be under 2MB.", "danger")
        return redirect(url_for("profile.my_profile"))

    ext = photo.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    photo.save(os.path.join(UPLOAD_FOLDER, filename))

    # ✅ Save only filename in DB
    user.profile_image = filename
    db.session.commit()

    flash("Profile photo updated!", "success")
    return redirect(url_for("profile.my_profile"))
