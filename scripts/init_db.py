import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app
from app.extensions import db
from app.models import User


def _pg_has_column(table: str, column: str) -> bool:
    check_sql = """
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = :table_name AND column_name = :column_name
    LIMIT 1;
    """
    with db.engine.connect() as conn:
        return (
            conn.execute(
                db.text(check_sql),
                {"table_name": table, "column_name": column},
            ).fetchone()
            is not None
        )


def ensure_users_columns():
    if db.engine.dialect.name != "postgresql":
        return

    if not _pg_has_column("users", "is_admin"):
        print("[MIGRATION] users.is_admin -> adicionando ...")
        with db.engine.connect() as conn:
            conn.execute(
                db.text(
                    "ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE;"
                )
            )
            conn.commit()
    else:
        print("[OK] users.is_admin já existe.")


def ensure_transactions_columns():
    """
    Auto-migration para schema legado da tabela transactions.
    Garante colunas principais e corrige colunas antigas (date/kind) que às vezes ficam NOT NULL.
    """
    if db.engine.dialect.name != "postgresql":
        return

    wanted = [
        ("type", "VARCHAR(3) NOT NULL DEFAULT 'OUT'"),
        ("amount", "NUMERIC(12,2) NOT NULL DEFAULT 0"),
        ("category", "VARCHAR(80) NOT NULL DEFAULT 'Geral'"),
        ("note", "VARCHAR(255)"),
        ("happened_on", "DATE NOT NULL DEFAULT CURRENT_DATE"),
        ("created_at", "TIMESTAMP NOT NULL DEFAULT NOW()"),
    ]

    # adiciona colunas que faltam
    for col, ddl in wanted:
        if not _pg_has_column("transactions", col):
            print(f"[MIGRATION] transactions.{col} -> adicionando ...")
            with db.engine.connect() as conn:
                conn.execute(db.text(f"ALTER TABLE transactions ADD COLUMN {col} {ddl};"))
                conn.commit()

    # Compat com schema antigo: coluna "date" NOT NULL
    if _pg_has_column("transactions", "date"):
        print("[MIGRATION] Compat: transactions.date detectada")
        with db.engine.connect() as conn:
            # preenche nulos
            conn.execute(db.text("""
                UPDATE transactions
                SET date = COALESCE(date, happened_on, CURRENT_DATE)
                WHERE date IS NULL;
            """))
            # default para novos
            conn.execute(db.text("""
                ALTER TABLE transactions
                ALTER COLUMN date SET DEFAULT CURRENT_DATE;
            """))
            # remove NOT NULL
            conn.execute(db.text("""
                ALTER TABLE transactions
                ALTER COLUMN date DROP NOT NULL;
            """))
            conn.commit()
        print("[OK] Compat: transactions.date ajustada (default + nullable).")

    # Compat com schema antigo: coluna "kind" NOT NULL
    if _pg_has_column("transactions", "kind"):
        print("[MIGRATION] Compat: transactions.kind detectada")
        with db.engine.connect() as conn:
            # preenche nulos (usa type se existir)
            conn.execute(db.text("""
                UPDATE transactions
                SET kind = COALESCE(kind, type, 'OUT')
                WHERE kind IS NULL;
            """))
            # default para novos
            conn.execute(db.text("""
                ALTER TABLE transactions
                ALTER COLUMN kind SET DEFAULT 'OUT';
            """))
            # remove NOT NULL
            conn.execute(db.text("""
                ALTER TABLE transactions
                ALTER COLUMN kind DROP NOT NULL;
            """))
            conn.commit()
        print("[OK] Compat: transactions.kind ajustada (default + nullable).")

    print("[OK] transactions schema conferido.")


def ensure_admin():
    admin_user = os.getenv("ADMIN_USER", "admin").strip()
    admin_pass = os.getenv("ADMIN_PASS", "admin123").strip()

    existing = User.query.filter_by(username=admin_user).first()
    if existing:
        try:
            existing.is_admin = True
            db.session.commit()
        except Exception:
            db.session.rollback()
        print(f"[OK] Admin '{admin_user}' já existe.")
        return

    u = User(username=admin_user, is_admin=True)
    u.set_password(admin_pass)
    db.session.add(u)
    db.session.commit()
    print(f"[OK] Admin criado: {admin_user} / {admin_pass}")


app = create_app()

with app.app_context():
    db.create_all()
    ensure_users_columns()
    ensure_transactions_columns()
    ensure_admin()
    print("DB initialized + schema fixed + admin ensured.")
