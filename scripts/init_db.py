import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app
from app.extensions import db


def ensure_admin_if_possible():
    """
    Cria admin padrão se o model User existir no app.models.
    Não quebra o deploy se você ainda não tiver criado o User.
    """
    try:
        from werkzeug.security import generate_password_hash
        from app.models import User
    except Exception as e:
        print(f"[SKIP] Não foi possível criar admin (User não disponível): {e}")
        return

    admin_user = os.getenv("ADMIN_USER", "admin").strip()
    admin_pass = os.getenv("ADMIN_PASS", "admin123").strip()

    # tenta detectar nome do campo de usuário
    username_field = "username" if hasattr(User, "username") else ("user" if hasattr(User, "user") else None)
    if not username_field:
        print("[SKIP] User model não tem campo username/user. Ajuste o init_db depois.")
        return

    existing = User.query.filter(getattr(User, username_field) == admin_user).first()
    if existing:
        print(f"Admin '{admin_user}' já existe. (ok)")
        return

    # tenta detectar o campo de senha
    pass_field = "password_hash" if hasattr(User, "password_hash") else ("password" if hasattr(User, "password") else None)
    if not pass_field:
        print("[SKIP] User model não tem password_hash/password. Ajuste o init_db depois.")
        return

    u = User(**{username_field: admin_user, pass_field: generate_password_hash(admin_pass)})

    # seta is_admin se existir
    if hasattr(u, "is_admin"):
        setattr(u, "is_admin", True)

    db.session.add(u)
    db.session.commit()
    print(f"Admin criado: {admin_user} / {admin_pass}")


app = create_app()

with app.app_context():
    db.create_all()
    ensure_admin_if_possible()
    print("DB initialized.")
