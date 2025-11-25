from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DATABASE_URL

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder="templates")

    # -----------------------------------------------
    # SUPABASE-COMPATIBELE DATABASE CONFIGURATIE
    # -----------------------------------------------

    # Zorg dat sslmode=require aanwezig is (vereist voor Supabase)
    db_url = DATABASE_URL
    if "sslmode" not in db_url:
        if "?" in db_url:
            db_url += "&sslmode=require"
        else:
            db_url += "?sslmode=require"

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Voorkomt MaxClientsInSessionMode fout
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 1,        # Supabase limit
        "max_overflow": 0,     # Geen extra connecties
        "pool_timeout": 30,
        "pool_recycle": 180,   # voorkom dode verbindingen
        "pool_pre_ping": True  # check of verbinding nog ok is
    }

    app.secret_key = "dev"

    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprints importeren
    from .auth_routes import auth_bp
    from .admin_routes import admin_bp
    from .driver_routes import driver_bp

    # Registreren
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(driver_bp)

    # Homepage → redirect naar login
    @app.route("/")
    def index():
        return redirect("/login")

    return app

