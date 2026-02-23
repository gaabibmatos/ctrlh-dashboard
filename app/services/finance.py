import datetime as dt
from sqlalchemy import func
from ..extensions import db
from ..models import Transaction, Budget, Category, Bill

def month_range(year:int, month:int):
    start = dt.date(year, month, 1)
    if month == 12:
        end = dt.date(year+1, 1, 1)
    else:
        end = dt.date(year, month+1, 1)
    return start, end

def sum_transactions(year:int, month:int, kind:str):
    start, end = month_range(year, month)
    q = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.kind == kind,
        Transaction.date >= start,
        Transaction.date < end
    )
    return float(q.scalar() or 0)

def expenses_by_category(year:int, month:int):
    start, end = month_range(year, month)
    rows = db.session.query(
        Category.name,
        func.coalesce(func.sum(Transaction.amount), 0)
    ).join(Category, Transaction.category_id == Category.id, isouter=True).filter(
        Transaction.kind == "expense",
        Transaction.date >= start,
        Transaction.date < end
    ).group_by(Category.name).all()

    out = []
    for name, total in rows:
        out.append((name or "Sem categoria", float(total or 0)))
    out.sort(key=lambda x: x[1], reverse=True)
    return out

def budgets_vs_real(year:int, month:int):
    start, end = month_range(year, month)
    budgets = db.session.query(Budget).filter_by(year=year, month=month).all()

    # totals real by category
    real_rows = dict(db.session.query(
        Transaction.category_id,
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.kind=="expense",
        Transaction.date>=start,
        Transaction.date<end
    ).group_by(Transaction.category_id).all())

    out = []
    for b in budgets:
        real = float(real_rows.get(b.category_id, 0) or 0)
        out.append({
            "category": b.category.name,
            "budget": float(b.amount or 0),
            "real": real,
            "delta": float(b.amount or 0) - real
        })

    # categories with real but no budget
    for cat_id, total in real_rows.items():
        if not any(x["category"] == (db.session.get(Category, cat_id).name if cat_id else "Sem categoria") for x in out):
            name = "Sem categoria" if cat_id is None else db.session.get(Category, cat_id).name
            out.append({"category": name, "budget": 0.0, "real": float(total or 0), "delta": -float(total or 0)})

    out.sort(key=lambda x: x["real"], reverse=True)
    return out

def bills_for_month(year:int, month:int):
    return db.session.query(Bill).filter_by(year=year, month=month).order_by(Bill.paid.asc(), Bill.due_date.asc().nullslast(), Bill.id.desc()).all()

def net_profit(year:int, month:int):
    income = sum_transactions(year, month, "income")
    expense = sum_transactions(year, month, "expense")
    return income - expense
