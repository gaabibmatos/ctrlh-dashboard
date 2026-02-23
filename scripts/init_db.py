from app import create_app
from app.extensions import db
from app.db import init_db

app = create_app()

with app.app_context():
    init_db()
    print("DB initialized.")
