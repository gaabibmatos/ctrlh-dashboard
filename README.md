# Ctrl-H | Dashboard de Operações (Flask)

Dashboard doméstico em 4 quadrantes:
1) Financeiro (Cash Flow)
2) Supply Chain (Estoque & Ativos)
3) Operacional (Escala de Tarefas)
4) Performance (Insights)

## Stack
- Python 3.10+
- Flask + SQLAlchemy + Flask-Login
- SQLite local (padrão)
- Postgres no Render via `DATABASE_URL`

## Rodando local (Windows / Linux / macOS)

### 1) Criar venv e instalar deps
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Configurar variáveis (opcional)
Copie `.env.example` para `.env` e ajuste se quiser.

Por padrão, sem `DATABASE_URL`, o app usa SQLite em `instance/ctrlh.db`.

### 3) Inicializar banco + seed demo (opcional)
```bash
python scripts/init_db.py
python scripts/seed_demo.py
```

### 4) Rodar
```bash
flask --app wsgi run --debug
# abre: http://127.0.0.1:5000
```

Login padrão (se você rodar `seed_demo.py`):
- usuário: `admin`
- senha: `admin123`

## Deploy no Render (GitHub)
No Render:
- Build Command:
  `pip install -r requirements.txt && python scripts/init_db.py`
- Start Command:
  `gunicorn wsgi:app`

Environment Vars:
- `DATABASE_URL` (Render Postgres)
- `SECRET_KEY` (uma chave forte)

> Observação: em produção, recomendamos Postgres (Render), porque o disco do web service pode não ser persistente.

## Estrutura
- `app/` aplicação Flask
- `scripts/` init do banco e seed
- `wsgi.py` entrypoint do Gunicorn
