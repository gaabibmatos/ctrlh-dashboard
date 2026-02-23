from flask import Blueprint, render_template
from datetime import datetime

from ..extensions import db

bp = Blueprint("dashboard", __name__)


def ym_now():
    now = datetime.now()
    return now.year, now.month


@bp.route("/")
def index():
    year, month = ym_now()

    # Por enquanto, dashboard não depende de models específicos.
    # (evita quebrar o deploy se o model financeiro ainda não existir)
    total = 0
    latest = []

    # Se no futuro existir um model com campos (amount, date), você pluga aqui.
    # Exemplo: Transaction / Expense / Lancamento etc.

    return render_template(
        "dashboard/index.html",
        total=total,
        latest=latest,
        year=year,
        month=month,
    )
