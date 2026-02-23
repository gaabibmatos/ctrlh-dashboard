import os
from flask import Flask
from dotenv import load_dotenv

from .extensions import db, login_manager
from .utils import build_db_uri

def create_app():
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = build_db_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from .routes.dashboard import bp as dashboard_bp
    from .routes.auth import bp as auth_bp
    from .routes.finance import bp as finance_bp
    from .routes.supply import bp as supply_bp
    from .routes.ops import bp as ops_bp
    from .routes.settings import bp as settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(supply_bp, url_prefix="/supply")
    app.register_blueprint(ops_bp, url_prefix="/ops")
    app.register_blueprint(settings_bp, url_prefix="/settings")

    return app
