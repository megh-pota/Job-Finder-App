
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import db
from app.models import User   # absolute import (safe)
# =========================
# Blueprints
# =========================
#auth_bp = Blueprint("auth", __name__ ,url_prefix="/auth")
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def home():
    if session.get("user_id"):
        role = session.get("user_type")
        if role == "admin":
            return redirect(url_for("admin_dash.dashboard"))
        elif role == "business":
            return redirect(url_for("company.view_my_company"))
        elif role == "job_seeker":
            return redirect(url_for("jobseeker.dashboard"))
        elif role == "employee":
            return redirect(url_for("employee.dashboard"))
    return redirect(url_for("auth.login"))

# =========================
# Debug Test Route
# =========================
@auth_bp.route("/ping")
def ping():
    return "AUTH BLUEPRINT WORKING"

# =========================
# Login Required Decorator
# =========================
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped

# =========================
# Role Required Decorator
# =========================
def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):

            if "user_id" not in session:
                flash("Please login first", "warning")
                return redirect(url_for("auth.login"))

            user = User.query.get(session.get("user_id"))

            if not user:
                session.clear()
                flash("Session expired. Please login again.", "danger")
                return redirect(url_for("auth.login"))

            # ✅ MULTI-ROLE CHECK
            if user.user_type not in roles:
                flash("Access denied.", "danger")
                return redirect(url_for("auth.login"))

            return view(*args, **kwargs)

        return wrapped
    return decorator

# =========================
# LOGIN
# =========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_type = request.form.get("user_type")  # EQUIRED (from login.html)

        if not email or not password or not user_type:
            flash("All fields are required", "warning")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

        # ✅ Role validation (IMPORTANT)
        if user.user_type != user_type:
            flash("Invalid role selected for this account", "danger")
            return redirect(url_for("auth.login"))

        session.clear()
        session["user_id"] = user.id
        session["user_type"] = user.user_type

        flash("Login successful", "success")

        # ✅ Role-based redirect
        if user.user_type == "admin":
            return redirect(url_for("admin_dash.dashboard"))

        elif user.user_type == "job_seeker":
            return redirect(url_for("jobseeker.dashboard"))

        elif user.user_type == "employee":
            return redirect(url_for("employee.dashboard"))

        elif user.user_type == "business":
            return redirect(url_for("company.view_my_company"))

        return redirect("/")

    return render_template("login.html")

# =========================
# REGISTER
# =========================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        user_type = request.form.get("user_type", "job_seeker")  # default role

        if not name or not email or not password:
            flash("All fields are required", "warning")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            user_type=user_type
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

# =========================
# LOGOUT
# =========================
@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))

