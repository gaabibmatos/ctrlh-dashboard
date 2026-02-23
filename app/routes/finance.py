import datetime as dt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..extensions import db
from ..models import Bill, Transaction, Category, Budget
from ..utils import ym_now
from ..services.finance import bills_for_month, budgets_vs_real

bp = Blueprint("finance", __name__)

@bp.get("/")
@login_required
def index():
    year, month = ym_now()
    bills = bills_for_month(year, month)
    budgets = budgets_vs_real(year, month)
    cats = db.session.query(Category).order_by(Category.name.asc()).all()
    return render_template("finance/index.html", year=year, month=month, bills=bills, budgets=budgets, cats=cats)

@bp.post("/bill/add")
@login_required
def add_bill():
    year, month = ym_now()
    desc = (request.form.get("description") or "").strip()
    amount = float(request.form.get("amount") or 0)
    due = request.form.get("due_date") or ""
    due_date = dt.date.fromisoformat(due) if due else None
    if not desc:
        flash("Descrição é obrigatória.", "warning")
        return redirect(url_for("finance.index"))
    b = Bill(year=year, month=month, description=desc, amount=amount, due_date=due_date, paid=False)
    db.session.add(b)
    db.session.commit()
    return redirect(url_for("finance.index"))

@bp.post("/bill/toggle/<int:bill_id>")
@login_required
def toggle_bill(bill_id):
    b = db.session.get(Bill, bill_id)
    if not b:
        flash("Conta não encontrada.", "danger")
        return redirect(url_for("finance.index"))
    b.paid = not b.paid
    db.session.commit()
    return redirect(url_for("finance.index"))

@bp.post("/tx/add")
@login_required
def add_tx():
    kind = request.form.get("kind") or "expense"
    date_str = request.form.get("date") or ""
    date = dt.date.fromisoformat(date_str) if date_str else dt.date.today()
    category_id = request.form.get("category_id") or ""
    category_id = int(category_id) if category_id else None
    desc = (request.form.get("description") or "").strip()
    amount = float(request.form.get("amount") or 0)

    if not desc:
        flash("Descrição é obrigatória.", "warning")
        return redirect(url_for("finance.index"))

    tx = Transaction(kind=kind, date=date, category_id=category_id, description=desc, amount=amount)
    db.session.add(tx)
    db.session.commit()
    return redirect(url_for("finance.index"))

@bp.post("/budget/set")
@login_required
def set_budget():
    year, month = ym_now()
    category_id = int(request.form.get("category_id"))
    amount = float(request.form.get("amount") or 0)
    b = db.session.query(Budget).filter_by(year=year, month=month, category_id=category_id).first()
    if not b:
        b = Budget(year=year, month=month, category_id=category_id, amount=amount)
        db.session.add(b)
    else:
        b.amount = amount
    db.session.commit()
    return redirect(url_for("finance.index"))
