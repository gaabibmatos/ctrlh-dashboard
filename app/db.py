from .extensions import db
from . import models  # noqa

def init_db():
    db.create_all()
