import datetime as dt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..extensions import db
from ..models import DailyTask, DeepClean, Owner

bp = Blueprint("ops", __name__)

@bp.get("/")
@login_required
def index():
    today = dt.date.today()
    owners = db.session.query(Owner).order_by(Owner.name.asc()).all()
    tasks = db.session.query(DailyTask).filter_by(date=today).order_by(DailyTask.done.asc(), DailyTask.id.desc()).all()
    deep = db.session.query(DeepClean).order_by(DeepClean.day_of_week.asc()).all()
    return render_template("ops/index.html", today=today, owners=owners, tasks=tasks, deep=deep)

@bp.post("/task/add")
@login_required
def add_task():
    title = (request.form.get("title") or "").strip()
    owner_id = request.form.get("owner_id") or ""
    owner_id = int(owner_id) if owner_id else None
    if not title:
        flash("Título é obrigatório.", "warning")
        return redirect(url_for("ops.index"))
    t = DailyTask(title=title, owner_id=owner_id, date=dt.date.today(), done=False)
    db.session.add(t)
    db.session.commit()
    return redirect(url_for("ops.index"))

@bp.post("/task/toggle/<int:task_id>")
@login_required
def toggle_task(task_id):
    t = db.session.get(DailyTask, task_id)
    if not t:
        flash("Tarefa não encontrada.", "danger")
        return redirect(url_for("ops.index"))
    t.done = not t.done
    db.session.commit()
    return redirect(url_for("ops.index"))

@bp.post("/deep/add")
@login_required
def add_deep():
    day_of_week = int(request.form.get("day_of_week"))
    area = (request.form.get("area") or "").strip()
    owner_id = request.form.get("owner_id") or ""
    owner_id = int(owner_id) if owner_id else None
    if not area:
        flash("Área é obrigatória.", "warning")
        return redirect(url_for("ops.index"))
    d = DeepClean(day_of_week=day_of_week, area=area, owner_id=owner_id)
    db.session.add(d)
    db.session.commit()
    return redirect(url_for("ops.index"))

@bp.post("/deep/done/<int:deep_id>")
@login_required
def deep_done(deep_id):
    d = db.session.get(DeepClean, deep_id)
    if not d:
        flash("Item não encontrado.", "danger")
        return redirect(url_for("ops.index"))
    d.last_done = dt.date.today()
    db.session.commit()
    return redirect(url_for("ops.index"))
