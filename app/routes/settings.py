from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..extensions import db
from ..models import Owner, Category

bp = Blueprint("settings", __name__)

@bp.get("/")
@login_required
def index():
    owners = db.session.query(Owner).order_by(Owner.name.asc()).all()
    cats = db.session.query(Category).order_by(Category.name.asc()).all()
    return render_template("settings/index.html", owners=owners, cats=cats)

@bp.post("/owner/add")
@login_required
def add_owner():
    name = (request.form.get("name") or "").strip()
    if not name:
        flash("Nome do responsável é obrigatório.", "warning")
        return redirect(url_for("settings.index"))
    if db.session.query(Owner).filter_by(name=name).first():
        flash("Responsável já existe.", "info")
        return redirect(url_for("settings.index"))
    db.session.add(Owner(name=name))
    db.session.commit()
    return redirect(url_for("settings.index"))

@bp.post("/category/add")
@login_required
def add_category():
    name = (request.form.get("name") or "").strip()
    if not name:
        flash("Nome da categoria é obrigatório.", "warning")
        return redirect(url_for("settings.index"))
    if db.session.query(Category).filter_by(name=name).first():
        flash("Categoria já existe.", "info")
        return redirect(url_for("settings.index"))
    db.session.add(Category(name=name))
    db.session.commit()
    return redirect(url_for("settings.index"))
