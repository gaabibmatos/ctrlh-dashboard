import datetime as dt
from app import create_app
from app.extensions import db
from app.models import User, Owner, Category, Budget, Bill, Transaction, StockItem, Asset, Acquisition, DailyTask, DeepClean

app = create_app()

def ensure_user():
    u = db.session.query(User).filter_by(username="admin").first()
    if not u:
        u = User(username="admin")
        u.set_password("admin123")
        db.session.add(u)

def run():
    ensure_user()

    # Owners
    for name in ["Ana", "João"]:
        if not db.session.query(Owner).filter_by(name=name).first():
            db.session.add(Owner(name=name))

    # Categories
    for name in ["Mercado", "Luz", "Internet", "Lazer", "Transporte"]:
        if not db.session.query(Category).filter_by(name=name).first():
            db.session.add(Category(name=name))

    db.session.commit()

    year = dt.date.today().year
    month = dt.date.today().month

    cat = {c.name: c for c in db.session.query(Category).all()}
    owner = {o.name: o for o in db.session.query(Owner).all()}

    # Budgets
    def up_budget(cat_name, amount):
        c = cat[cat_name]
        b = db.session.query(Budget).filter_by(year=year, month=month, category_id=c.id).first()
        if not b:
            b = Budget(year=year, month=month, category_id=c.id, amount=amount)
            db.session.add(b)
        else:
            b.amount = amount

    up_budget("Mercado", 1000)
    up_budget("Luz", 250)
    up_budget("Internet", 150)
    up_budget("Lazer", 200)

    # Bills
    if db.session.query(Bill).filter_by(year=year, month=month).count() == 0:
        db.session.add(Bill(year=year, month=month, description="Aluguel", amount=1200, due_date=dt.date.today().replace(day=10), paid=False))
        db.session.add(Bill(year=year, month=month, description="Internet", amount=120, due_date=dt.date.today().replace(day=5), paid=True))
        db.session.add(Bill(year=year, month=month, description="Mercado (cartão)", amount=850, due_date=dt.date.today().replace(day=20), paid=False))

    # Transactions
    if db.session.query(Transaction).count() == 0:
        db.session.add(Transaction(kind="income", date=dt.date.today().replace(day=1), description="Salário", amount=4500))
        db.session.add(Transaction(kind="expense", date=dt.date.today().replace(day=3), category_id=cat["Internet"].id, description="Internet", amount=120))
        db.session.add(Transaction(kind="expense", date=dt.date.today().replace(day=7), category_id=cat["Luz"].id, description="Conta de luz", amount=310))
        db.session.add(Transaction(kind="expense", date=dt.date.today().replace(day=12), category_id=cat["Mercado"].id, description="Mercado", amount=850))

    # Stock
    if db.session.query(StockItem).count() == 0:
        db.session.add(StockItem(name="Arroz", unit="kg", qty=0, min_qty=2))
        db.session.add(StockItem(name="Sabão em pó", unit="un", qty=1, min_qty=2))
        db.session.add(StockItem(name="Detergente", unit="un", qty=1, min_qty=1))

    # Assets
    if db.session.query(Asset).count() == 0:
        db.session.add(Asset(name="Geladeira", status="OK", note=""))
        db.session.add(Asset(name="Ar Condicionado", status="ATENCAO", note="Limpeza em 15 dias"))
        db.session.add(Asset(name="Airfryer", status="TROCAR", note=""))

    # Acquisition
    if not db.session.query(Acquisition).first():
        db.session.add(Acquisition(name="Notebook", target_amount=3500, saved_amount=1400))

    # Daily tasks (today)
    today = dt.date.today()
    if db.session.query(DailyTask).filter_by(date=today).count() == 0:
        db.session.add(DailyTask(date=today, title="Lavar louça", owner_id=owner["Ana"].id, done=False))
        db.session.add(DailyTask(date=today, title="Retirar lixo", owner_id=owner["João"].id, done=False))
        db.session.add(DailyTask(date=today, title="Varrer sala", owner_id=owner["Ana"].id, done=True))

    # Deep clean schedule
    if db.session.query(DeepClean).count() == 0:
        db.session.add(DeepClean(day_of_week=0, area="Cozinha", owner_id=owner["João"].id))
        db.session.add(DeepClean(day_of_week=2, area="Banheiros", owner_id=owner["Ana"].id))
        db.session.add(DeepClean(day_of_week=4, area="Área externa", owner_id=owner["João"].id))

    db.session.commit()
    print("Seed demo created. Login admin/admin123")

def main():
    with app.app_context():
        run()

if __name__ == "__main__":
    main()
