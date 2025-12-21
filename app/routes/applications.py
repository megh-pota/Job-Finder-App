from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app import db
from app.models import Application, Job
from app.routes.auth import login_required, role_required

from app.ml.resume_matcher import calculate_match_score
from app.ml.recommender import extract_text_from_pdf
from app.ml.skill_extractor import extract_skills


applications_bp = Blueprint("applications", __name__, url_prefix="/applications")


# ===============================
# CONFIG
# ===============================
UPLOAD_FOLDER = "app/static/uploads/resumes"
ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ===============================
# APPLY FOR A JOB
# (JOB SEEKER + EMPLOYEE)
# ===============================
@applications_bp.route("/apply/<int:job_id>", methods=["POST"])
@login_required
@role_required("job_seeker", "employee")
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)

    user_id = session.get("user_id")
    user_role = session.get("user_type")

    # Prevent duplicate applications
    existing = Application.query.filter_by(
        job_id=job_id,
        seeker_user_id=user_id
    ).first()

    if existing:
        flash("You have already applied for this job.", "warning")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    resume = request.files.get("resume")

    if not resume or resume.filename == "":
        flash("Please upload a resume (PDF).", "danger")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    if not allowed_file(resume.filename):
        flash("Only PDF resumes are allowed.", "danger")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    # File size validation
    resume.seek(0, os.SEEK_END)
    size = resume.tell()
    resume.seek(0)

    if size > MAX_FILE_SIZE:
        flash("Resume must be under 2 MB.", "danger")
        return redirect(url_for("jobs.job_detail", job_id=job_id))

    # Save resume
    filename = secure_filename(resume.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_filename = f"{user_id}_{timestamp}_{filename}"
    saved_path = os.path.join(UPLOAD_FOLDER, saved_filename)

    resume.save(saved_path)

    # ===============================
    # ML PROCESSING
    # ===============================
    match_score = calculate_match_score(
        saved_path,
        job.description
    )

    resume_text = extract_text_from_pdf(saved_path)
    skills = extract_skills(resume_text)

    # ===============================
    # SAVE APPLICATION
    # ===============================
    # Store WEB path (ALWAYS with /)
    web_path = f"uploads/resumes/{saved_filename}"
    application = Application(
        job_id=job_id,
        seeker_user_id=user_id,
        resume_file_path=web_path,
        match_score=match_score,
        skills=", ".join(skills)
    )

    db.session.add(application)
    db.session.commit()

    flash(
        f"Application submitted successfully! Match score: {match_score}%",
        "success"
    )

    # Redirect by role
    if user_role == "employee":
        return redirect(url_for("employee.applied_jobs"))
    else:
        return redirect(url_for("applications.my_applications"))


# ===============================
# JOB SEEKER — MY APPLICATIONS
# ===============================
@applications_bp.route("/my")
@login_required
@role_required("job_seeker","employee")
def my_applications():
    applications = (
        Application.query
        .filter_by(seeker_user_id=session["user_id"])
        .order_by(Application.applied_at.desc())
        .all()
    )

    return render_template(
        "applications.html",
        applications=applications
    )


# ===============================
# BUSINESS — VIEW APPLICATIONS
# ===============================
@applications_bp.route("/job/<int:job_id>")
@login_required
@role_required("business")
def view_job_applications(job_id):
    job = Job.query.get_or_404(job_id)

    if job.posted_by_user_id != session.get("user_id"):
        flash("You do not have permission to view applications.", "danger")
        return redirect(url_for("jobs.my_jobs"))

    applications = (
        Application.query
        .filter_by(job_id=job_id)
        .order_by(Application.match_score.desc())  # 🔥 ML RANKING
        .all()
    )

    return render_template(
        "job_applications.html",
        job=job,
        applications=applications
    )
