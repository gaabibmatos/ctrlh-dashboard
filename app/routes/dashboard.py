from flask import Blueprint, render_template
from datetime import datetime

from ..models import Expense
from ..extensions import db

bp = Blueprint("dashboard", __name__)


# =========================
# Helper local (sem utils)
# =========================
def ym_now():
    now = datetime.now()
    return now.year, now.month


@bp.route("/")
def index():
    year, month = ym_now()

    # Total gasto no mês atual
    total = (
        db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0))
        .filter(
            db.extract("year", Expense.date) == year,
            db.extract("month", Expense.date) == month,
        )
        .scalar()
    )

    # Últimas despesas
    latest = (
        Expense.query.order_by(Expense.date.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        total=total,
        latest=latest,
        year=year,
        month=month,
    )
