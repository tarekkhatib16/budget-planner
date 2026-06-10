# budget-planner

A personal budget planner replacing a spreadsheet: a yearly view of a monthly
budget plan, and a weekly expense tracker that spreads each month's spending
budget across its weeks. All amounts are GBP, stored as integer pence.

## Backend (FastAPI)

```
backend/
├── api/
│   ├── core/          # settings loaded from .env
│   ├── dependencies/  # request-scoped DB session + service providers
│   ├── domain/        # pure business maths (weeks, allowances, savings)
│   ├── exceptions/    # app errors + HTTP mapping
│   ├── models/        # SQLAlchemy ORM models
│   ├── repositories/  # data access (queries only)
│   ├── routers/       # HTTP endpoints (thin)
│   ├── schemas/       # Pydantic request/response contracts
│   ├── services/      # use-cases orchestrating repos + domain
│   ├── shared/        # cross-cutting enums/constants
│   └── utils/         # small helpers (dates)
├── database/          # engine, session factory, Base, seed script
└── alembic/           # migrations
```

### Setup & run

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/alembic upgrade head          # create/upgrade the SQLite schema
.venv/bin/python -m database.seed       # default categories from the spreadsheet
.venv/bin/uvicorn api.main:app --reload --port 8001
```

Interactive docs at http://localhost:8001/docs

### Tests

```bash
cd backend && .venv/bin/python -m pytest tests
```

### API at a glance

| Endpoint | Purpose |
| --- | --- |
| `GET /api/v1/budgets/{year}` | Yearly grid: categories by group, monthly totals, savings |
| `PUT /api/v1/budgets/{year}/{month}/categories/{id}` | Set one budget cell |
| `GET /api/v1/months/{year}/{month}` | Weekly tracker: allowance/spent/saved per week |
| `GET/POST/DELETE /api/v1/expenses` | Log and remove expenses |
| `GET/POST/PATCH/DELETE /api/v1/categories` | Manage budget rows |

## Frontend

TypeScript + React PWA (to be built) in `frontend/`.
