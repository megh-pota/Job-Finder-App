from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
#
# class Task(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     title = db.Column(db.String(100),nullable = False)
#     status = db.Column(db.String(20), default = "Pending")
#
# class User(db.Model):
#     __tablename__ = "users"
#
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), nullable=False)
#     email = db.Column(db.String(150), unique=True, nullable=False)
#     password_hash = db.Column(db.String(255), nullable=False)
#
#     # user_type such as: "seeker", "employer", "admin", etc.
#     user_type = db.Column(db.String(50), nullable=False, default="seeker")
#
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------
# USERS
# ---------------------------------------------------------------------
class User(db.Model):
    __tablename__ ='users'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), nullable=False, default="seeker") # admin, employer, seeker
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    companies = db.relationship("Company", backref="employer", lazy=True)
    jobs_posted = db.relationship("Job", backref="poster", lazy=True)

    applications = db.relationship(
        "Application",
        foreign_keys="Application.seeker_user_id",
        backref="seeker",
        lazy=True
    )
    profile_image = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# ---------------------------------------------------------------------
# COMPANIES
# ---------------------------------------------------------------------
class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text)
    industry = db.Column(db.String(120))
    website = db.Column(db.String(200))

    employer_user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False,unique=True ) # IMPORTANT

    jobs = db.relationship("Job", backref="company", lazy=True)

# ---------------------------------------------------------------------
# JOBS
# ---------------------------------------------------------------------
class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary_range = db.Column(db.String(100))
    location = db.Column(db.String(150))
    job_type = db.Column(db.String(50))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    posted_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    applications = db.relationship("Application", backref="job", lazy=True)
    categories = db.relationship("JobCategory", secondary="job_skills",
                                 back_populates="jobs")
# ---------------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------------
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    seeker_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    resume_file_path = db.Column(db.String(255))
    status = db.Column(db.String(50), default="Pending")
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    # ✅ NEW (ML SCORE)
    match_score = db.Column(db.Float)  # percentage (0–100)
    skills = db.Column(db.Text)  # comma-separated


# ---------------------------------------------------------------------
# JOB CATEGORIES
# ---------------------------------------------------------------------
class JobCategory(db.Model):
    __tablename__ = "job_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    jobs = db.relationship("Job",
                           secondary="job_skills",
                           back_populates="categories")

# ---------------------------------------------------------------------
# JOB SKILL (Mapping Table)
# ---------------------------------------------------------------------
# class JobSkill(db.Model):
#     __tablename__ = "job_skills"
#
#     id = db.Column(db.Integer, primary_key=True)
#     job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
#     category_id = db.Column(db.Integer, db.ForeignKey("job_categories.id"), nullable=False)
job_skills = db.Table(
    "job_skills",
    db.Column("job_id", db.Integer, db.ForeignKey("jobs.id"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("job_categories.id"), primary_key=True)
)

