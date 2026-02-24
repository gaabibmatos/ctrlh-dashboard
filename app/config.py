import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    raw = (os.getenv("DATABASE_URL") or "").strip()

    if raw:
        # Render costuma entregar postgres://...  (vamos normalizar)
        if raw.startswith("postgres://"):
            raw = raw.replace("postgres://", "postgresql://", 1)

        # Força SQLAlchemy a usar psycopg3 (não psycopg2)
        # Opção A: manter postgresql:// e adicionar ?driver=psycopg
        if "driver=" not in raw:
            raw += ("&" if "?" in raw else "?") + "driver=psycopg"

        SQLALCHEMY_DATABASE_URI = raw
    else:
        # Local
        SQLALCHEMY_DATABASE_URI = "sqlite:///ctrlh.db"
