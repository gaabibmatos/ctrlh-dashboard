from .extensions import db
from . import models  # noqa: F401

def init_db():
    db.create_all()
