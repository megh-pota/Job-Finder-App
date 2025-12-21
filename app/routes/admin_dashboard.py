from flask import Blueprint, render_template
from sqlalchemy import func

from app.routes.auth import login_required, role_required
from app.models import User, Company, Job, Application
from app import db

admin_dash_bp = Blueprint("admin_dash", __name__, url_prefix="/admin")


@admin_dash_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():

    # ===============================
    # USER ROLE DISTRIBUTION
    # ===============================
    role_counts = dict(
        db.session.query(
            User.user_type,
            func.count(User.id)
        )
        .group_by(User.user_type)
        .all()
    )

    # Ensure all roles exist (safe for charts)
    for role in ["admin", "business", "employee", "job_seeker", "suspended"]:
        role_counts.setdefault(role, 0)

    # ===============================
    # JOBS PER COMPANY
    # ===============================
    jobs_by_company = (
        db.session.query(
            Company.name,
            func.count(Job.id)
        )
        .outerjoin(Job)
        .group_by(Company.id)
        .all()
    )

    company_names = [row[0] for row in jobs_by_company]
    job_counts = [row[1] for row in jobs_by_company]

    # ===============================
    # APPLICATIONS PER JOB
    # ===============================
    apps_by_job = (
        db.session.query(
            Job.title,
            func.count(Application.id)
        )
        .outerjoin(Application)
        .group_by(Job.id)
        .all()
    )

    job_titles = [row[0] for row in apps_by_job]
    apps_per_job = [row[1] for row in apps_by_job]

    # ===============================
    # GLOBAL STATS
    # ===============================
    total_users = User.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()

    avg_match_score = (
        db.session.query(func.avg(Application.match_score))
        .scalar()
    )
    avg_match_score = round(avg_match_score or 0, 2)

    # ===============================
    # TOP SKILLS (ML ANALYTICS)
    # ===============================
    skills_rows = (
        db.session.query(Application.skills)
        .filter(Application.skills.isnot(None))
        .all()
    )

    skill_count = {}
    for row in skills_rows:
        for skill in row[0].split(","):
            skill = skill.strip()
            if skill:
                skill_count[skill] = skill_count.get(skill, 0) + 1

    return render_template(
        "dashboards/admin_dashboard.html",

        # charts
        role_counts=role_counts,
        company_names=company_names,
        job_counts=job_counts,
        job_titles=job_titles,
        apps_per_job=apps_per_job,

        # stats
        total_users=total_users,
        total_jobs=total_jobs,
        total_applications=total_applications,
        avg_match_score=avg_match_score,

        # ML
        skill_count=skill_count
    )
