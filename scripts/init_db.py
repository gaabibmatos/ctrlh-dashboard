import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app
from app.db_init import init_db   # <-- TROCOU AQUI

app = create_app()

with app.app_context():
    init_db()
    print("DB initialized.")
