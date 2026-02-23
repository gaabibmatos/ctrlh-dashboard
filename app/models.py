import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .extensions import db, login_manager

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow, nullable=False)

class User(UserMixin, db.Model, TimestampMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, raw: str):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class Owner(db.Model):
    __tablename__ = "owners"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

class Budget(db.Model):
    __tablename__ = "budgets"
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    amount = db.Column(db.Numeric(12,2), nullable=False, default=0)

    category = db.relationship("Category")

    __table_args__ = (db.UniqueConstraint("year","month","category_id", name="uq_budget_ym_cat"),)

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=dt.date.today)
    kind = db.Column(db.String(10), nullable=False)  # income | expense
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(12,2), nullable=False, default=0)

    category = db.relationship("Category")

class Bill(db.Model):
    __tablename__ = "bills"
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(12,2), nullable=False, default=0)
    due_date = db.Column(db.Date, nullable=True)
    paid = db.Column(db.Boolean, nullable=False, default=False)

class StockItem(db.Model):
    __tablename__ = "stock_items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), unique=True, nullable=False)
    unit = db.Column(db.String(20), nullable=False, default="un")
    qty = db.Column(db.Numeric(12,2), nullable=False, default=0)
    min_qty = db.Column(db.Numeric(12,2), nullable=False, default=1)

class Asset(db.Model):
    __tablename__ = "assets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="OK")  # OK | ATENCAO | TROCAR
    next_maintenance = db.Column(db.Date, nullable=True)
    note = db.Column(db.String(255), nullable=True)

class Acquisition(db.Model):
    __tablename__ = "acquisitions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    target_amount = db.Column(db.Numeric(12,2), nullable=False, default=0)
    saved_amount = db.Column(db.Numeric(12,2), nullable=False, default=0)

class DailyTask(db.Model):
    __tablename__ = "daily_tasks"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=dt.date.today)
    title = db.Column(db.String(180), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.id"), nullable=True)
    done = db.Column(db.Boolean, nullable=False, default=False)

    owner = db.relationship("Owner")

class DeepClean(db.Model):
    __tablename__ = "deep_clean"
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Seg ... 6=Dom
    area = db.Column(db.String(180), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.id"), nullable=True)
    last_done = db.Column(db.Date, nullable=True)

    owner = db.relationship("Owner")
