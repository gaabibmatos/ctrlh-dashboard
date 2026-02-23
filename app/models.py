from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Transaction(db.Model):
    """
    Lançamento financeiro simples:
    - type: 'OUT' (gasto) ou 'IN' (entrada)
    - amount: valor positivo
    - category: texto livre por enquanto (depois virará tabela)
    - happened_on: data do lançamento
    """
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(3), nullable=False, default="OUT")  # OUT / IN
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    category = db.Column(db.String(80), nullable=False, default="Geral")
    note = db.Column(db.String(255), nullable=True)

    happened_on = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Transaction {self.type} {self.amount} {self.category} {self.happened_on}>"
