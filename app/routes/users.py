from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth import login_required, role_required
from app.models import User
from app import db
from werkzeug.security import generate_password_hash

users_bp = Blueprint("users", __name__, url_prefix="/users")


# =========================
# ADVANCED USER LIST VIEW
# =========================
@users_bp.route("/")
@login_required
@role_required("admin")
def users_list():
    search = request.args.get("search")
    role = request.args.get("role")
    page = request.args.get("page", 1, type=int)

    query = User.query

    # SEARCH USER
    if search:
        query = query.filter(
            User.name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%")
        )

    # FILTER BY ROLE
    if role and role != "all":
        query = query.filter_by(user_type=role)

    # PAGINATION (10 per page)
    users_page = query.paginate(page=page, per_page=10)

    return render_template("users.html",
                           users=users_page.items,
                           pagination=users_page,
                           search=search,
                           role=role)


# =========================
# VIEW USER DETAILS
# =========================
@users_bp.route("/view/<int:user_id>")
@login_required
@role_required("admin")
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("users_view.html", user=user)


# =========================
# EDIT USER DETAILS
# =========================
@users_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.name = request.form["name"]
        user.email = request.form["email"]
        user.user_type = request.form["user_type"]

        db.session.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for("users.users_list"))

    return render_template("users_edit.html", user=user)


# =========================
# DELETE USER (ADMIN SAFE)
# =========================
@users_bp.route("/delete/<int:user_id>")
@login_required
@role_required("admin")
def delete_user(user_id):
    # Prevent deleting own admin account
    if user_id == session.get("user_id"):
        flash("You cannot delete your own admin account!", "danger")
        return redirect(url_for("users.users_list"))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash("User deleted!", "danger")
    return redirect(url_for("users.users_list"))


# =========================
# SUSPEND USER
# =========================
@users_bp.route("/suspend/<int:user_id>")
@login_required
@role_required("admin")
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    user.user_type = "suspended"

    db.session.commit()
    flash("User suspended!", "warning")
    return redirect(url_for("users.users_list"))


# =========================
# ACTIVATE USER
# =========================
@users_bp.route("/activate/<int:user_id>")
@login_required
@role_required("admin")
def activate_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.user_type == "suspended":
        user.user_type = "job_seeker"

    db.session.commit()
    flash("User activated!", "success")
    return redirect(url_for("users.users_list"))


# =========================
# ADMIN RESET USER PASSWORD
# =========================
@users_bp.route("/reset-password/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin")
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)

    new_pass = request.form.get("new_password")
    user.password_hash = generate_password_hash(new_pass)

    db.session.commit()
    flash("Password reset successfully!", "success")
    return redirect(url_for("users.view_user", user_id=user.id))
