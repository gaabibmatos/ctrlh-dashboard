from datetime import date, datetime
from decimal import Decimal

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from ..extensions import db
from ..models import Transaction

bp = Blueprint("finance", __name__, url_prefix="/finance")


def ym_now():
    now = datetime.now()
    return now.year, now.month


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    year, month = ym_now()
    error = None

    if request.method == "POST":
        t_type = (request.form.get("type") or "OUT").strip().upper()
        category = (request.form.get("category") or "Geral").strip()[:80]
        note = (request.form.get("note") or "").strip()[:255]

        amount_raw = (request.form.get("amount") or "").replace(",", ".").strip()
        date_raw = (request.form.get("happened_on") or "").strip()

        try:
            amount = Decimal(amount_raw)
            if amount <= 0:
                raise ValueError("amount <= 0")
        except Exception:
            error = "Valor inválido. Ex: 25.90"
            amount = None

        try:
            happened_on = date.fromisoformat(date_raw) if date_raw else date.today()
        except Exception:
            error = "Data inválida."
            happened_on = None

        if t_type not in ("IN", "OUT"):
            error = "Tipo inválido."

        if not error:
        tx = Transaction(
            type=t_type,
            amount=amount,
            category=category or "Geral",
            note=note or None,
            happened_on=happened_on,
        )

        # compatibilidade: se existir coluna antiga "date", seta também
            if hasattr(Transaction, "date"):
            tx.date = happened_on

            db.session.add(tx)
            db.session.commit()
            return redirect(url_for("finance.index"))

    # lista do mês
    items = (
        Transaction.query
        .filter(db.extract("year", Transaction.happened_on) == year)
        .filter(db.extract("month", Transaction.happened_on) == month)
        .order_by(Transaction.happened_on.desc(), Transaction.id.desc())
        .all()
    )

    total_out = sum([float(x.amount) for x in items if x.type == "OUT"])
    total_in = sum([float(x.amount) for x in items if x.type == "IN"])

    return render_template(
        "finance/index.html",
        items=items,
        total_out=total_out,
        total_in=total_in,
        year=year,
        month=month,
        error=error,
    )


@bp.route("/delete/<int:tx_id>", methods=["POST"])
@login_required
def delete(tx_id: int):
    tx = Transaction.query.get_or_404(tx_id)
    db.session.delete(tx)
    db.session.commit()
    return redirect(url_for("finance.index"))
