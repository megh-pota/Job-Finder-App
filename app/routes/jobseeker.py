from flask import Blueprint, render_template, session
from app.models import User
from app.routes.auth import login_required, role_required
from app.ml.utils import get_recommendations_for_user

jobseeker_bp = Blueprint("jobseeker", __name__, url_prefix="/jobseeker")


import os
from app.models import Application, Job,User
from app.ml.resume_matcher import calculate_match_score

@jobseeker_bp.route("/dashboard")
@login_required
@role_required("job_seeker")
def dashboard():
    user = User.query.get(session.get("user_id"))

    # =========================
    # PROFILE STATUS (REAL)
    # =========================
    profile_active = bool(
        user.name and
        user.email and
        user.profile_image
    )

    # =========================
    # RESUME STATUS (REAL FILE CHECK)
    # =========================
    latest_application = (
        Application.query
        .filter_by(seeker_user_id=user.id)
        .order_by(Application.applied_at.desc())
        .first()
    )

    resume_uploaded = False
    resume_path = None

    if latest_application and latest_application.resume_file_path:
        resume_path = latest_application.resume_file_path
        resume_uploaded = os.path.exists(resume_path)

    # =========================
    # ML ENGINE STATUS
    # =========================
    ml_enabled = profile_active and resume_uploaded

    # =========================
    # JOB RECOMMENDATIONS
    # =========================
    recommendations = []

    if ml_enabled:
        jobs = Job.query.all()

        for job in jobs:
            score = calculate_match_score(
                resume_path,
                job.description
            )

            if score >= 40:
                recommendations.append({
                    "job": job,
                    "match_percent": score
                })

        recommendations.sort(
            key=lambda x: x["match_percent"],
            reverse=True
        )

        recommendations = recommendations[:5]

    return render_template(
        "dashboards/jobseeker_dashboard.html",
        user=user,
        profile_active=profile_active,
        resume_uploaded=resume_uploaded,
        ml_enabled=ml_enabled,
        recommendations=recommendations
    )
