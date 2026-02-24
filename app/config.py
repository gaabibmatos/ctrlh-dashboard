import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

    if DATABASE_URL:
        # Render costuma entregar postgres:// mas SQLAlchemy pede postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///ctrlh.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
