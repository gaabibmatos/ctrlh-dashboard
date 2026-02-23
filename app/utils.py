import os
from datetime import datetime


# ===============================
# DATABASE URI (Render + Local)
# ===============================
def build_db_uri():
    url = os.getenv("DATABASE_URL", "").strip()

    # Se não existir DATABASE_URL → usa SQLite local
    if not url:
        return "sqlite:///instance/ctrlh.db"

    # Render às vezes fornece postgres:// (formato antigo)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Força uso do driver psycopg3 (evita psycopg2)
    if url.startswith("postgresql://") and "+psycopg" not in url and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url


# ===============================
# Helpers de data (Ano/Mês)
# ===============================
def ym_now():
    """Retorna (year, month) do momento atual."""
    now = datetime.now()
    return now.year, now.month


def ym_prev(year: int, month: int):
    """Retorna (year, month) do mês anterior."""
    if month == 1:
        return year - 1, 12
    return year, month - 1


def ym_label(year, month):
    """Formata Ano/Mês como MM/YYYY"""
    try:
        return f"{int(month):02d}/{int(year)}"
    except Exception:
        return ""


# ===============================
# FORMATADORES PARA JINJA
# ===============================
def brl(value):
    """Formata número como moeda brasileira."""
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def week_label(date_obj):
    """Formata semana ISO."""
    if isinstance(date_obj, datetime):
        return f"Semana {date_obj.isocalendar()[1]}"
    return ""
