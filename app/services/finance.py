from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..extensions import db
from ..models import Transaction

bp = Blueprint("finance", __name__, url_prefix="/finance")


def _parse_amount_br(raw: str) -> Decimal:
    if raw is None:
        raise InvalidOperation("amount vazio")
    s = raw.strip()
    if not s:
        raise InvalidOperation("amount vazio")

    s = s.replace("R$", "").replace(" ", "")

    # 1.234,56 -> 1234.56
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    return Decimal(s)


def _month_range(year: int, month: int) -> tuple[date, date]:
    first = date(year, month, 1)
    if month == 12:
        nxt = date(year + 1, 1, 1)
    else:
        nxt = date(year, month + 1, 1)
    return first, nxt


def _get_ym() -> tuple[str, int, int]:
    ym = (request.args.get("ym") or "").strip()
    if not ym:
        ym = date.today().strftime("%Y-%m")

    try:
        year = int(ym.split("-")[0])
        month = int(ym.split("-")[1])
    except Exception:
        year, month = date.today().year, date.today().month
        ym = f"{year:04d}-{month:02d}"
    return ym, year, month


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    ym, year, month = _get_ym()

    # CREATE
    if request.method == "POST":
        t_type = (request.form.get("type") or "OUT").strip().upper()
        category = (request.form.get("category") or "Geral").strip()
        note = (request.form.get("note") or "").strip()
        amount_raw = request.form.get("amount") or ""
        happened_on_raw = (request.form.get("happened_on") or "").strip()

        try:
            amount = _parse_amount_br(amount_raw)
        except InvalidOperation:
            flash("Valor inválido. Ex: 1200,50", "error")
            return redirect(url_for("finance.index", ym=ym))

        try:
            happened_on = (
                datetime.strptime(happened_on_raw, "%Y-%m-%d").date()
                if happened_on_raw
                else date.today()
            )
        except Exception:
            flash("Data inválida. Use o seletor de data.", "error")
            return redirect(url_for("finance.index", ym=ym))

        if t_type not in ("IN", "OUT"):
            t_type = "OUT"

        try:
            tx = Transaction(
                type=t_type,
                amount=amount,
                category=category or "Geral",
                note=note or None,
                happened_on=happened_on,
            )

            # compat com schemas antigos (se existirem no model)
            if hasattr(Transaction, "date"):
                tx.date = happened_on  # type: ignore[attr-defined]
            if hasattr(Transaction, "kind"):
                tx.kind = t_type  # type: ignore[attr-defined]
            if hasattr(Transaction, "description"):
                tx.description = note or category or ""  # type: ignore[attr-defined]

            db.session.add(tx)
            db.session.commit()
            flash("Lançamento salvo ✅", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar: {e}", "error")

        return redirect(url_for("finance.index", ym=ym))

    # READ (list)
    start, end = _month_range(year, month)
    items = (
        Transaction.query
        .filter(Transaction.happened_on >= start)
        .filter(Transaction.happened_on < end)
        .order_by(Transaction.happened_on.desc(), Transaction.id.desc())
        .all()
    )

    total_in = sum((t.amount for t in items if getattr(t, "type", "OUT") == "IN"), Decimal("0"))
    total_out = sum((t.amount for t in items if getattr(t, "type", "OUT") != "IN"), Decimal("0"))
    net = total_in - total_out

    return render_template(
        "finance/index.html",
        ym=ym,
        year=year,
        month=month,
        items=items,
        total_in=total_in,
        total_out=total_out,
        net=net,
    )


@bp.route("/<int:tx_id>/edit", methods=["GET", "POST"])
@login_required
def edit(tx_id: int):
    ym, year, month = _get_ym()

    tx = Transaction.query.get_or_404(tx_id)

    if request.method == "POST":
        t_type = (request.form.get("type") or tx.type or "OUT").strip().upper()
        category = (request.form.get("category") or tx.category or "Geral").strip()
        note = (request.form.get("note") or "").strip()
        amount_raw = request.form.get("amount") or ""
        happened_on_raw = (request.form.get("happened_on") or "").strip()

        try:
            amount = _parse_amount_br(amount_raw)
        except InvalidOperation:
            flash("Valor inválido. Ex: 1200,50", "error")
            return redirect(url_for("finance.edit", tx_id=tx_id, ym=ym))

        try:
            happened_on = (
                datetime.strptime(happened_on_raw, "%Y-%m-%d").date()
                if happened_on_raw
                else tx.happened_on
            )
        except Exception:
            flash("Data inválida. Use o seletor de data.", "error")
            return redirect(url_for("finance.edit", tx_id=tx_id, ym=ym))

        if t_type not in ("IN", "OUT"):
            t_type = "OUT"

        try:
            tx.type = t_type
            tx.amount = amount
            tx.category = category or "Geral"
            tx.note = note or None
            tx.happened_on = happened_on

            # compat schemas antigos (se existirem no model)
            if hasattr(Transaction, "date"):
                tx.date = happened_on  # type: ignore[attr-defined]
            if hasattr(Transaction, "kind"):
                tx.kind = t_type  # type: ignore[attr-defined]
            if hasattr(Transaction, "description"):
                tx.description = note or category or ""  # type: ignore[attr-defined]

            db.session.commit()
            flash("Lançamento atualizado ✅", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar: {e}", "error")

        return redirect(url_for("finance.index", ym=ym))

    # GET: form de edição
    return render_template("finance/edit.html", ym=ym, tx=tx)


@bp.route("/<int:tx_id>/delete", methods=["POST"])
@login_required
def delete(tx_id: int):
    ym, year, month = _get_ym()

    tx = Transaction.query.get_or_404(tx_id)
    try:
        db.session.delete(tx)
        db.session.commit()
        flash("Lançamento excluído 🗑️", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir: {e}", "error")

    return redirect(url_for("finance.index", ym=ym))
