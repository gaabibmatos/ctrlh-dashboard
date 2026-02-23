from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required

from ..models import User

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()

        u = User.query.filter_by(username=username).first()
        if not u or not u.check_password(password):
            error = "Usuário ou senha inválidos."
        else:
            login_user(u)
            return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html", error=error)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
