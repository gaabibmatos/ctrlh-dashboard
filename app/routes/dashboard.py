import datetime as dt
from flask import Blueprint, render_template, request
from flask_login import login_required
from ..utils import ym_now
from ..services.finance import bills_for_month, budgets_vs_real, net_profit
from ..services.supply import critical_stock, asset_status_summary, acquisition_current
from ..services.ops import daily_tasks, deep_clean_schedule
from ..services.performance import expense_efficiency, health_score

bp = Blueprint("dashboard", __name__)

@bp.get("/")
@login_required
def index():
    today = dt.date.today()
    year, month = ym_now()

    # finance
    bills = bills_for_month(year, month)
    bvr = budgets_vs_real(year, month)[:5]
    sobra = net_profit(year, month)

    # supply
    crit = critical_stock()
    assets = asset_status_summary()[:6]
    acq = acquisition_current()

    # ops
    tasks = daily_tasks(today)
    deep = deep_clean_schedule()

    # perf
    eff = expense_efficiency(year, month)[:5]
    score, reasons = health_score(today, year, month)

    return render_template(
        "dashboard.html",
        today=today, year=year, month=month,
        bills=bills, bvr=bvr, sobra=sobra,
        crit=crit, assets=assets, acq=acq,
        tasks=tasks, deep=deep,
        eff=eff, score=score, reasons=reasons
    )
