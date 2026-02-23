import datetime as dt
from sqlalchemy import func
from ..extensions import db
from ..models import Bill, DailyTask, DeepClean, StockItem, Transaction, Category
from .finance import month_range, expenses_by_category

def expense_efficiency(year:int, month:int):
    return expenses_by_category(year, month)

def health_score(week_date: dt.date, year:int, month:int):
    # Base 10, penalidades:
    # - contas vencidas e pendentes: -1.0 cada (até -4)
    # - daily tasks pendentes na semana: -0.2 cada (até -2)
    # - deep clean atrasado no dia da semana (se existe item p/ dia e não feito essa semana): -0.8 cada (até -2.4)
    # - itens críticos de estoque: -0.4 cada (até -1.6)
    score = 10.0
    reasons = []

    monday = week_date - dt.timedelta(days=week_date.weekday())
    sunday = monday + dt.timedelta(days=6)

    # bills overdue unpaid
    overdue = db.session.query(Bill).filter(Bill.paid==False, Bill.due_date != None, Bill.due_date < week_date).all()
    if overdue:
        penalty = min(4.0, 1.0 * len(overdue))
        score -= penalty
        reasons.append(f"{len(overdue)} conta(s) vencida(s) e pendente(s) (-{penalty:.1f})")

    # daily tasks pending in week
    pending_tasks = db.session.query(DailyTask).filter(DailyTask.date >= monday, DailyTask.date <= sunday, DailyTask.done==False).count()
    if pending_tasks:
        penalty = min(2.0, 0.2 * pending_tasks)
        score -= penalty
        reasons.append(f"{pending_tasks} tarefa(s) diária(s) pendente(s) na semana (-{penalty:.1f})")

    # deep clean expected on weekday
    dow = week_date.weekday()
    deep_today = db.session.query(DeepClean).filter_by(day_of_week=dow).all()
    if deep_today:
        # consider atrasado se last_done < monday
        late = [d for d in deep_today if (d.last_done is None or d.last_done < monday)]
        if late:
            penalty = min(2.4, 0.8 * len(late))
            score -= penalty
            reasons.append(f"{len(late)} item(ns) de Deep Clean sem execução na semana (-{penalty:.1f})")

    # critical stock
    stock = db.session.query(StockItem).all()
    crit = 0
    for it in stock:
        try:
            if float(it.qty or 0) <= float(it.min_qty or 0):
                crit += 1
        except Exception:
            pass
    if crit:
        penalty = min(1.6, 0.4 * crit)
        score -= penalty
        reasons.append(f"{crit} item(ns) em falta/nível crítico (-{penalty:.1f})")

    score = max(0.0, min(10.0, score))
    return score, reasons
