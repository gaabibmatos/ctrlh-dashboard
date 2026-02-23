import os
from flask import Flask
from flask_login import current_user
from dotenv import load_dotenv

from .extensions import db, login_manager
from .utils import build_db_uri

load_dotenv()


def create_app():
    app = Flask(__name__)

    # SECRET_KEY (Render env ou fallback)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    # DATABASE_URL automático (Render Postgres ou SQLite local)
    app.config["SQLALCHEMY_DATABASE_URI"] = build_db_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Blueprints ATIVOS (mínimo)
    from .routes.auth import bp as auth_bp
    from .routes.dashboard import bp as dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # Redireciona login view
    login_manager.login_view = "auth.login"

    return app
