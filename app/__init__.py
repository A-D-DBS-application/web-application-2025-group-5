# app/__init__.py

from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import DATABASE_URL
from babel.dates import format_date


db = SQLAlchemy()
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = "auth.login"   # Waar naartoe als je niet ingelogd bent


def create_app():
    app = Flask(__name__, template_folder="templates")

    # -----------------------------------------------
    # SUPABASE DATABASE CONFIG
    # -----------------------------------------------
    db_url = DATABASE_URL
    if "sslmode" not in db_url:
        db_url += "&sslmode=require" if "?" in db_url else "?sslmode=require"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Supabase low-connection-limit config
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 1,
        "max_overflow": 0,
        "pool_timeout": 30,
        "pool_recycle": 180,
        "pool_pre_ping": True,
    }

    # Nodig voor Flask-login sessions
    app.secret_key = "dev"   # Vervang later door een echte secure key

    # -----------------------------------------------
    # INITIALIZE EXTENSIONS
    # -----------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # -----------------------------------------------
    # USER LOADER (Flask-Login)
    # -----------------------------------------------
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -----------------------------------------------
    # nederlandse datum
    # ----------------------------------------------- 
    @app.template_filter("nl_date")
    def nl_date(date):
        return format_date(date, format="EEEE d MMMM", locale="nl")
    # -----------------------------------------------
    # BLUEPRINTS
    # -----------------------------------------------
    from .auth_routes import auth_bp
    from .admin_routes import admin_bp
    from .driver_routes import driver_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(driver_bp)

    # -----------------------------------------------
    # HOME REDIRECT
    # -----------------------------------------------
    @app.route("/")
    def index():
        return redirect("/login")

    return app
