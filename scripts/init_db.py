import os
import sys

# garante que a raiz do projeto esteja no PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User  # precisa existir no seu models.py


def ensure_admin():
    """
    Cria um usuário admin padrão (apenas se não existir).
    Você pode sobrescrever via env vars:
      ADMIN_USER, ADMIN_PASS
    """
    admin_user = os.getenv("ADMIN_USER", "admin").strip()
    admin_pass = os.getenv("ADMIN_PASS", "admin123").strip()

    existing = User.query.filter_by(username=admin_user).first()
    if existing:
        print(f"Admin '{admin_user}' já existe. (ok)")
        return

    u = User(
        username=admin_user,
        password_hash=generate_password_hash(admin_pass),
        is_admin=True if hasattr(User, "is_admin") else True,
    )

    db.session.add(u)
    db.session.commit()
    print(f"Admin criado: {admin_user} / {admin_pass}")


app = create_app()

with app.app_context():
    db.create_all()
    ensure_admin()
    print("DB initialized + admin ensured.")
