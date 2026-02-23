import datetime as dt
from ..extensions import db
from ..models import StockItem, Asset, Acquisition

def critical_stock():
    items = db.session.query(StockItem).order_by(StockItem.name.asc()).all()
    crit = []
    for it in items:
        try:
            if float(it.qty or 0) <= float(it.min_qty or 0):
                crit.append(it)
        except Exception:
            pass
    return crit

def asset_status_summary():
    return db.session.query(Asset).order_by(Asset.name.asc()).all()

def acquisition_current():
    acq = db.session.query(Acquisition).first()
    return acq
