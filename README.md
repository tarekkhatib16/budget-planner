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

## Frontend (React + TypeScript PWA)

```
frontend/src/
├── api/         # fetch client + typed wrappers mirroring the backend schemas
├── components/  # BudgetGrid, BudgetCellInput, WeekCard, ExpenseForm, ErrorNote
├── hooks/       # useAsync (load/reload around fetches)
├── pages/       # YearPage (budget grid), MonthPage (weekly tracker)
└── utils/       # money (pence <-> pounds), dates
```

### Run (with the backend running on port 8001)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — `/api` is proxied to the backend. `npm run build`
type-checks and produces `dist/`.

### Add to iPhone home screen

The dev server listens on the LAN (`host: true`). On an iPhone on the same
wifi, open `http://<your-mac-ip>:5173` in Safari (find the IP via System
Settings → Wi-Fi), then Share → **Add to Home Screen**. The manifest makes it
launch standalone (no Safari chrome) with the £ icon.
