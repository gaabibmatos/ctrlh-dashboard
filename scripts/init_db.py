import os
import sys

# garante que a raiz do projeto esteja no PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app
from app.extensions import db
from app.db import init_db

app = create_app()

with app.app_context():
    init_db()
    print("DB initialized.")
