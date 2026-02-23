import datetime as dt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..extensions import db
from ..models import StockItem, Asset, Acquisition

bp = Blueprint("supply", __name__)

@bp.get("/")
@login_required
def index():
    stock = db.session.query(StockItem).order_by(StockItem.name.asc()).all()
    assets = db.session.query(Asset).order_by(Asset.name.asc()).all()
    acq = db.session.query(Acquisition).first()
    return render_template("supply/index.html", stock=stock, assets=assets, acq=acq)

@bp.post("/stock/add")
@login_required
def add_stock():
    name = (request.form.get("name") or "").strip()
    unit = (request.form.get("unit") or "un").strip()
    qty = float(request.form.get("qty") or 0)
    min_qty = float(request.form.get("min_qty") or 1)
    if not name:
        flash("Nome do item é obrigatório.", "warning")
        return redirect(url_for("supply.index"))
    it = db.session.query(StockItem).filter_by(name=name).first()
    if it:
        it.qty = qty
        it.min_qty = min_qty
        it.unit = unit
    else:
        it = StockItem(name=name, unit=unit, qty=qty, min_qty=min_qty)
        db.session.add(it)
    db.session.commit()
    return redirect(url_for("supply.index"))

@bp.post("/asset/add")
@login_required
def add_asset():
    name = (request.form.get("name") or "").strip()
    status = (request.form.get("status") or "OK").strip().upper()
    next_maint = request.form.get("next_maintenance") or ""
    note = (request.form.get("note") or "").strip()
    if not name:
        flash("Nome do ativo é obrigatório.", "warning")
        return redirect(url_for("supply.index"))
    nm = dt.date.fromisoformat(next_maint) if next_maint else None
    a = db.session.query(Asset).filter_by(name=name).first()
    if a:
        a.status = status
        a.next_maintenance = nm
        a.note = note
    else:
        a = Asset(name=name, status=status, next_maintenance=nm, note=note)
        db.session.add(a)
    db.session.commit()
    return redirect(url_for("supply.index"))

@bp.post("/acq/set")
@login_required
def set_acq():
    name = (request.form.get("name") or "").strip()
    target = float(request.form.get("target_amount") or 0)
    saved = float(request.form.get("saved_amount") or 0)
    if not name:
        flash("Nome da aquisição é obrigatório.", "warning")
        return redirect(url_for("supply.index"))
    acq = db.session.query(Acquisition).first()
    if not acq:
        acq = Acquisition(name=name, target_amount=target, saved_amount=saved)
        db.session.add(acq)
    else:
        acq.name = name
        acq.target_amount = target
        acq.saved_amount = saved
    db.session.commit()
    return redirect(url_for("supply.index"))
