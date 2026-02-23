import datetime as dt
from ..extensions import db
from ..models import DailyTask, DeepClean

def daily_tasks(date: dt.date):
    return db.session.query(DailyTask).filter_by(date=date).order_by(DailyTask.done.asc(), DailyTask.id.desc()).all()

def deep_clean_schedule():
    return db.session.query(DeepClean).order_by(DeepClean.day_of_week.asc(), DeepClean.id.asc()).all()
