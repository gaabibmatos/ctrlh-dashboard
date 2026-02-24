import os
from flask import Flask
from dotenv import load_dotenv

from .extensions import db, login_manager
from .utils import build_db_uri

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    from .routes.auth import bp as auth_bp
    from .routes.dashboard import bp as dashboard_bp
    from .routes.finance import bp as finance_bp  # <<<
    # (se tiver supply/ops/performance, mantém também)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(finance_bp)  # <<<

    return app
