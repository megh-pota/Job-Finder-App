from flask import Blueprint, render_template, session
from app.routes.auth import login_required, role_required
from app.models import User
dashboard_bp = Blueprint("dashboard", __name__)

PERMISSIONS = {
    "admin": {
        "can_manage_users": True,
        "can_manage_jobs": True,
        "can_apply": False,
        "can_edit_profile": True,
    },
    "job_seeker": {
        "can_manage_users": False,
        "can_manage_jobs": False,
        "can_apply": True,
        "can_edit_profile": True,
    },
    "employee": {
        "can_manage_users": False,
        "can_manage_jobs": False,
        "can_apply": False,
        "can_edit_profile": True,
    },
    "business": {
        "can_manage_users": False,
        "can_manage_jobs": True,  # can post jobs
        "can_apply": False,
        "can_edit_profile": True,
    }
}


# Helper: Get logged-in user
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)

# =========================
# ADMIN DASHBOARD
# =========================
@dashboard_bp.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    return render_template(
        "dashboards/admin_dashboard.html",
        user=current_user(),
        permissions=PERMISSIONS["admin"]
    )


# =========================
# JOB SEEKER DASHBOARD
# =========================
@dashboard_bp.route("/jobseeker/dashboard")
@role_required("job_seeker")
def jobseeker_dashboard():
    return render_template(
        "dashboards/jobseeker_dashboard.html",
        user=current_user(),
        permissions=PERMISSIONS["job_seeker"]
    )


# =========================
# EMPLOYEE DASHBOARD
# =========================
@dashboard_bp.route("/employee/dashboard")
@role_required("employee")
def employee_dashboard():
    return render_template(
        "dashboards/employee_dashboard.html",
        user=current_user(),
        permissions=PERMISSIONS["employee"]
    )


# =========================
# BUSINESS DASHBOARD
# =========================
@dashboard_bp.route("/business/dashboard")
@role_required("business")
def business_dashboard():
    return render_template(
        "dashboards/business_dashboard.html",
        user=current_user(),
        permissions=PERMISSIONS["business"]
    )
