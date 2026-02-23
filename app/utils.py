import os
import pathlib
import datetime as dt

def build_db_uri() -> str:
    # If DATABASE_URL is set (Render Postgres), use it.
    # Otherwise, default to local SQLite in instance/ctrlh.db
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        # Render often provides postgres:// - SQLAlchemy expects postgresql://
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url

    instance_path = pathlib.Path(__file__).resolve().parent.parent / "instance"
    instance_path.mkdir(parents=True, exist_ok=True)
    db_path = instance_path / "ctrlh.db"
    return f"sqlite:///{db_path.as_posix()}"

def brl(value) -> str:
    try:
        v = float(value or 0)
    except Exception:
        v = 0.0
    # Format simple pt-BR style (sem depender de locale do SO)
    s = f"{v:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

def ym_now():
    today = dt.date.today()
    return today.year, today.month

def ym_label(year:int, month:int) -> str:
    months = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    return f"{months[month-1]}/{year}"

def week_label(date: dt.date) -> str:
    # Monday..Sunday range label
    monday = date - dt.timedelta(days=date.weekday())
    sunday = monday + dt.timedelta(days=6)
    return f"{monday.strftime('%d/%m')} a {sunday.strftime('%d/%m')}"
