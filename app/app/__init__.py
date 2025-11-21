from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_URL

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates")

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "dev"

    db.init_app(app)

    # Initialize Flask-Migrate (Alembic) for schema migrations
    try:
        from flask_migrate import Migrate

        Migrate(app, db)
    except Exception:
        # If Flask-Migrate isn't installed or fails, continue — migrations are optional.
        pass

    # Blueprints importeren
    from .auth_routes import auth_bp
    from .admin_routes import admin_bp
    from .driver_routes import driver_bp
    from .preview_routes import preview_bp

    # Registreren
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(driver_bp)
    app.register_blueprint(preview_bp)

    # Homepage (verplicht)
    @app.route("/")
    def index():
        return "App draait! Ga naar /login om in te loggen."

    return app
