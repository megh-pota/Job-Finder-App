from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

#create Database Object globally
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates")
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "mykeys")
    #app.config['SQLALCHEMY'] = 'sqlite:///'+os.path.join(basedir,'todo.db')
    #app.config['SQLALCHEMY_DATABASE_URI'] = ''
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL","mysql+pymysql://root:tom404@localhost:3306/TODO")

    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # db.__init__(app)
    db.init_app(app)
    from app.routes.auth import auth_bp
    from app.routes.company import company_bp
    from app.routes.jobs import jobs_bp
    from app.routes.applications import applications_bp
    from app.routes.profile import profile_bp
    from app.routes.users import users_bp
    from app.routes.admin_dashboard import admin_dash_bp
    from app.routes.employee import employee_bp
    from app.routes.jobseeker import jobseeker_bp

    app.register_blueprint(jobseeker_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_dash_bp)

    return app
