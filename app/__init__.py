# app/__init__.py

from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DATABASE_URL

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder="templates")

    # -----------------------------------------------
    # SUPABASE DATABASE CONFIG
    # -----------------------------------------------
    db_url = DATABASE_URL
    if "sslmode" not in db_url:
        db_url += "&sslmode=require" if "?" in db_url else "?sslmode=require"

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Supabase low connection limits
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 1,
        "max_overflow": 0,
        "pool_timeout": 30,
        "pool_recycle": 180,
        "pool_pre_ping": True
    }

    app.secret_key = "dev"

    db.init_app(app)
    migrate.init_app(app, db)

    # -----------------------------------------------
    # BLUEPRINTS
    # -----------------------------------------------
    from .auth_routes import auth_bp
    from .admin_routes import admin_bp
    from .driver_routes import driver_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(driver_bp)

    # Home redirect
    @app.route("/")
    def index():
        return redirect("/login")

    return app
