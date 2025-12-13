# app/__init__.py

from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import DATABASE_URL

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


# -------------------------------------------------------
# NEDERLANDSE DATUMFILTER
# -------------------------------------------------------
def format_dutch_date(value):
    """Zet een Python date/datetime om naar Nederlandse datum."""
    maanden = [
        "januari", "februari", "maart", "april", "mei", "juni",
        "juli", "augustus", "september", "oktober", "november", "december"
    ]
    dagen = [
        "maandag", "dinsdag", "woensdag", "donderdag",
        "vrijdag", "zaterdag", "zondag"
    ]

    try:
        dagnaam = dagen[value.weekday()]
        maandnaam = maanden[value.month - 1]
        return f"{dagnaam.capitalize()} {value.day} {maandnaam}"
    except Exception:
        return value  # fallback: toon originele waarde


# -------------------------------------------------------
# CREATE APP
# -------------------------------------------------------
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

    # Login sessions key
    app.secret_key = "dev"

    # -----------------------------------------------
    # INITIALIZE EXTENSIONS
    # -----------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # -----------------------------------------------
    # REGISTER JINJA FILTER
    # -----------------------------------------------
    app.jinja_env.filters["nl_date"] = format_dutch_date

    # -----------------------------------------------
    # USER LOADER
    # -----------------------------------------------
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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
    # HOME ROUTE
    # -----------------------------------------------
    @app.route("/")
    def index():
        return redirect("/login")

    return app
