from flask import Blueprint, render_template, session
from app.models import User, Job, Application
from app.routes.auth import login_required, role_required

employee_bp = Blueprint("employee", __name__, url_prefix="/employee")


# ===============================
# EMPLOYEE DASHBOARD
# ===============================
@employee_bp.route("/dashboard")
@login_required
@role_required("employee")
def dashboard():
    user = User.query.get(session.get("user_id"))

    # ✅ Correct: COUNT only
    applied_count = Application.query.filter_by(
        seeker_user_id=user.id
    ).count()

    # ✅ Recent 5 applications
    recent_applications = (
        Application.query
        .filter_by(seeker_user_id=user.id)
        .order_by(Application.applied_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboards/employee_dashboard.html",
        user=user,
        applied_count=applied_count,
        applications=recent_applications
    )


# ===============================
# EMPLOYEE APPLIED JOBS (FULL LIST)
# ===============================
@employee_bp.route("/applications")
@login_required
@role_required("employee")
def applied_jobs():
    user_id = session.get("user_id")

    applications = (
        Application.query
        .filter_by(seeker_user_id=user_id)   # ✅ FIXED
        .order_by(Application.applied_at.desc())
        .all()
    )

    return render_template(
        "employee/applied_jobs.html",
        applications=applications
    )
