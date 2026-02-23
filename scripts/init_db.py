import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app
from app.extensions import db
from app.models import User


def ensure_admin():
    admin_user = os.getenv("ADMIN_USER", "admin").strip()
    admin_pass = os.getenv("ADMIN_PASS", "admin123").strip()

    existing = User.query.filter_by(username=admin_user).first()
    if existing:
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
    ensure_admin()
    print("DB initialized + admin ensured.")
