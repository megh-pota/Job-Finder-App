from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.ml.similar_jobs import find_similar_jobs
from app import db
from app.models import Job, Company,User
from app.routes.auth import role_required, login_required

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")

# folder for optional job attachments (not strictly required)
UPLOAD_FOLDER = "uploads/job_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)




# LIST ALL JOBS (PUBLIC)
from app.ml.skill_extractor import extract_skills

@jobs_bp.route("/")
def jobs_list():
    selected_skill = request.args.get("skill")

    all_jobs = Job.query.all()

    # 🔥 Collect skills dynamically from job descriptions
    skill_set = set()
    for job in all_jobs:
        if job.description:
            skills = extract_skills(job.description)
            skill_set.update(skills)

    skills = sorted(skill_set)

    # 🔎 Filter jobs if skill selected
    if selected_skill:
        jobs = [
            job for job in all_jobs
            if job.description and
               selected_skill.lower() in job.description.lower()
        ]
    else:
        jobs = all_jobs

    return render_template(
        "jobs.html",
        jobs=jobs,
        skills=skills,              # ✅ consistent name
        selected_skill=selected_skill
    )



@jobs_bp.route("/<int:job_id>")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    all_jobs = Job.query.all()

    similar_jobs = find_similar_jobs(job, all_jobs)

    return render_template(
        "job_detail.html",
        job=job,
        similar_jobs=similar_jobs
    )


# CREATE NEW JOB (BUSINESS ONLY)
@jobs_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("business")
def create_job():
    # restrict to companies owned by current user
    companies = Company.query.filter_by(employer_user_id=session["user_id"]).all()

    if not companies:
        flash("You must create a company before posting jobs.", "warning")
        return redirect(url_for("company.create_company"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        salary = request.form.get("salary")
        location = request.form.get("location")
        job_type = request.form.get("job_type")
        company_id = request.form.get("company_id")

        # simple validation
        if not title or not description or not location or not job_type or not company_id:
            flash("Please complete all required fields.", "danger")
            return redirect(url_for("jobs.create_job"))

        # ensure selected company belongs to user
        company = Company.query.filter_by(id=company_id, employer_user_id=session["user_id"]).first()
        if not company:
            flash("Invalid company selection.", "danger")
            return redirect(url_for("jobs.create_job"))

        job = Job(
            title=title,
            description=description,
            salary_range=salary,
            location=location,
            job_type=job_type,
            company_id=company.id,
            posted_by_user_id=session["user_id"]
        )

        db.session.add(job)
        db.session.commit()

        flash("Job posted successfully!", "success")
        return redirect(url_for("jobs.jobs_list"))

    return render_template("job_create.html", companies=companies)


# EDIT JOB (BUSINESS ONLY, OWNER)
@jobs_bp.route("/edit/<int:job_id>", methods=["GET", "POST"])
@login_required
@role_required("business")
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)

    # ensure ownership
    if job.posted_by_user_id != session["user_id"]:
        flash("You do not have permission to edit this job.", "danger")
        return redirect(url_for("jobs.my_jobs"))

    companies = Company.query.filter_by(employer_user_id=session["user_id"]).all()

    if request.method == "POST":
        job.title = request.form.get("title")
        job.description = request.form.get("description")
        job.salary_range = request.form.get("salary")
        job.location = request.form.get("location")
        job.job_type = request.form.get("job_type")
        company_id = request.form.get("company_id")

        # ensure company belongs to user
        company = Company.query.filter_by(id=company_id, employer_user_id=session["user_id"]).first()
        if not company:
            flash("Invalid company selection.", "danger")
            return redirect(url_for("jobs.edit_job", job_id=job.id))

        job.company_id = company.id

        db.session.commit()
        flash("Job updated successfully.", "success")
        return redirect(url_for("jobs.my_jobs"))

    return render_template("job_edit.html", job=job, companies=companies)


# DELETE JOB (BUSINESS ONLY, OWNER)
@jobs_bp.route("/delete/<int:job_id>", methods=["POST", "GET"])
@login_required
@role_required("business")
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)

    # ensure ownership
    if job.posted_by_user_id != session["user_id"]:
        flash("You do not have permission to delete this job.", "danger")
        return redirect(url_for("jobs.my_jobs"))

    if request.method == "POST":
        db.session.delete(job)
        db.session.commit()
        flash("Job deleted.", "success")
        return redirect(url_for("jobs.my_jobs"))

    # if GET, show confirmation page (optional)
    return render_template("job_delete_confirm.html", job=job)


# BUSINESS: VIEW MY POSTED JOBS
@jobs_bp.route("/my")
@login_required
@role_required("business")
def my_jobs():
    jobs = Job.query.filter_by(posted_by_user_id=session["user_id"]).order_by(Job.posted_at.desc()).all()
    return render_template("my_jobs.html", jobs=jobs)
