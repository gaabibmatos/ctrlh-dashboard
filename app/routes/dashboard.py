from flask import Blueprint, render_template
from datetime import datetime
from flask_login import login_required

bp = Blueprint("dashboard", __name__)


def ym_now():
    now = datetime.now()
    return now.year, now.month


@bp.route("/")
@login_required
def index():
    year, month = ym_now()

    # Placeholder por enquanto
    total = 0
    latest = []

    return render_template(
        "dashboard/index.html",
        total=total,
        latest=latest,
        year=year,
        month=month,
    )
