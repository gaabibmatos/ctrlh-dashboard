from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from ..extensions import db
from ..models import User

bp = Blueprint("auth", __name__)

@bp.get("/login")
def login():
    return render_template("auth/login.html")

@bp.post("/login")
def login_post():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    user = db.session.query(User).filter_by(username=username).first()
    if not user or not user.check_password(password):
        flash("Usuário ou senha inválidos.", "danger")
        return redirect(url_for("auth.login"))
    login_user(user)
    return redirect(url_for("dashboard.index"))

@bp.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
