import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app
from app.extensions import db
from app.models import User


def ensure_users_columns():
    """
    Ajusta schema legado no Postgres (Render) sem usar migrations.
    - Garante coluna is_admin
    """
    engine = db.engine
    dialect = engine.dialect.name

    # Só faz sentido em Postgres; no SQLite tanto faz.
    if dialect != "postgresql":
        return

    # Checa se coluna is_admin existe
    check_sql = """
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'users' AND column_name = 'is_admin'
    LIMIT 1;
    """

    with engine.connect() as conn:
        exists = conn.execute(db.text(check_sql)).fetchone() is not None
        if not exists:
            print("[MIGRATION] Adicionando coluna users.is_admin ...")
            conn.execute(db.text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE;"))
            conn.commit()
        else:
            print("[OK] Coluna users.is_admin já existe.")


def ensure_admin():
    admin_user = os.getenv("ADMIN_USER", "admin").strip()
    admin_pass = os.getenv("ADMIN_PASS", "admin123").strip()

    existing = User.query.filter_by(username=admin_user).first()
    if existing:
        # garante que seja admin
        try:
            existing.is_admin = True
            db.session.commit()
        except Exception:
            db.session.rollback()
        print(f"Admin '{admin_user}' já existe. (ok)")
        return

    u = User(username=admin_user, is_admin=True)
    u.set_password(admin_pass)
    db.session.add(u)
    db.session.commit()
    print(f"Admin criado: {admin_user} / {admin_pass}")


app = create_app()

with app.app_context():
    db.create_all()
    ensure_users_columns()
    ensure_admin()
    print("DB initialized + schema fixed + admin ensured.")
