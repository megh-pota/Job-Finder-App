from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from app.models import Company, User
from app import db
from app.routes.auth import role_required, login_required
company_bp = Blueprint("company", __name__, url_prefix="/companies")


# =========================
# LIST ALL COMPANIES (PUBLIC)
# =========================
@company_bp.route("/")
def companies_list():
    companies = Company.query.all()
    return render_template("companies.html", companies=companies)


# =========================
# CREATE NEW COMPANY (BUSINESS ACCOUNT ONLY)
# =========================
@company_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("business")  # IMPORTANT: Correct role
def create_company():
    user_id = session.get("user_id")

    # Check if this user already owns a company
    existing_company = Company.query.filter_by(employer_user_id=user_id).first()
    if existing_company:
        flash("You already have a registered company.", "warning")
        return redirect(url_for("company.view_my_company"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        industry = request.form.get("industry")
        website = request.form.get("website")

        # Validate form
        if not name or not description or not industry:
            flash("Please fill out all required fields.", "danger")
            return redirect(url_for("company.create_company"))

        company = Company(
            name=name,
            description=description,
            industry=industry,
            website=website,
            employer_user_id=user_id
        )

        db.session.add(company)
        db.session.commit()

        flash("Company created successfully!", "success")
        return redirect(url_for("company.view_my_company"))

    return render_template("company_create.html")


# =========================
# VIEW COMPANY CREATED BY CURRENT BUSINESS USER
# =========================
@company_bp.route("/my-company")
@login_required
@role_required("business")
def view_my_company():
    user_id = session.get("user_id")
    company = Company.query.filter_by(employer_user_id=user_id).first()

    if not company:
        flash("You have not created a company yet.", "info")
        return redirect(url_for("company.create_company"))

    return render_template("company_view.html", company=company)


# =========================
# EDIT COMPANY DETAILS (ONLY OWNER)
# =========================
@company_bp.route("/edit", methods=["GET", "POST"])
@login_required
@role_required("business")
def edit_company():
    user_id = session.get("user_id")
    company = Company.query.filter_by(employer_user_id=user_id).first()

    if not company:
        flash("No company found to edit.", "warning")
        return redirect(url_for("company.create_company"))

    if request.method == "POST":
        company.name = request.form.get("name")
        company.description = request.form.get("description")
        company.industry = request.form.get("industry")
        company.website = request.form.get("website")

        db.session.commit()
        flash("Company updated successfully!", "success")
        return redirect(url_for("company.view_my_company"))

    return render_template("company_edit.html", company=company)
