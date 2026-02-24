from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # compat: se existir no banco, ok; se não existir, init_db cria
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    # IN ou OUT
    type = db.Column(db.String(3), nullable=False, default="OUT")

    # Numeric no Postgres / Decimal em Python
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    category = db.Column(db.String(80), nullable=False, default="Geral")
    note = db.Column(db.String(255), nullable=True)

    happened_on = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
