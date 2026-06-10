# budget-planner

A personal budget planner replacing a spreadsheet: a yearly view of a monthly
budget plan, and a weekly expense tracker that spreads each month's spending
budget across its weeks. All amounts are GBP, stored as integer pence.
Multi-user with email/password login; every row is scoped to its owner.

## Backend (FastAPI)

```
backend/
├── api/
│   ├── core/          # settings (.env) + password hashing / JWT helpers
│   ├── dependencies/  # request-scoped DB session, current user, services
│   ├── domain/        # pure business maths (weeks, allowances, savings)
│   ├── exceptions/    # app errors + HTTP mapping
│   ├── models/        # SQLAlchemy ORM models (User, Category, BudgetEntry, Expense)
│   ├── repositories/  # data access (queries only, always user-scoped)
│   ├── routers/       # HTTP endpoints (thin)
│   ├── schemas/       # Pydantic request/response contracts
│   ├── services/      # use-cases orchestrating repos + domain
│   ├── shared/        # cross-cutting enums/constants, default categories
│   └── utils/         # small helpers (dates)
├── database/          # engine, session factory, Base
└── alembic/           # migrations
```

### Setup & run

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
cp .env.example .env                    # then adjust if needed
.venv/bin/alembic upgrade head          # create/upgrade the schema
.venv/bin/uvicorn api.main:app --reload --port 8001
```

Interactive docs at http://localhost:8001/docs. Registering an account
creates the default spreadsheet categories automatically.

### Tests

```bash
cd backend && .venv/bin/python -m pytest tests
```

### API at a glance

All endpoints except `/auth/register` and `/auth/login` require an
`Authorization: Bearer <token>` header.

| Endpoint | Purpose |
| --- | --- |
| `POST /api/v1/auth/register` | Create an account (returns a JWT + seeds default categories) |
| `POST /api/v1/auth/login` | Exchange email/password for a JWT |
| `GET /api/v1/auth/me` | Current user |
| `GET /api/v1/budgets/{year}` | Yearly grid: categories by group, monthly totals, savings |
| `PUT /api/v1/budgets/{year}/{month}/categories/{id}` | Set one budget cell |
| `GET /api/v1/months/{year}/{month}` | Weekly tracker: allowance/spent/saved per week |
| `GET/POST/DELETE /api/v1/expenses` | Log and remove expenses |
| `GET/POST/PATCH/DELETE /api/v1/categories` | Manage budget rows |

## Frontend (React + TypeScript PWA)

```
frontend/src/
├── api/         # fetch client (attaches the JWT) + typed wrappers
├── auth/        # AuthContext (login/register/logout) + token storage
├── components/  # SectionCard, BudgetCellInput, WeekCard, ExpenseForm, ErrorNote
├── hooks/       # useAsync (load/reload around fetches)
├── pages/       # LoginPage, BudgetPage (two-month section cards), MonthPage (weekly tracker)
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

## Using Supabase (Postgres)

The backend is database-agnostic: point `DATABASE_URL` at Postgres and the
same Alembic migrations apply (verified against Postgres 16).

1. Create a Supabase project, then Dashboard → **Connect** and copy the
   **session pooler** connection string (the direct connection is IPv6-only
   and unreachable from most hosts, including Render's free tier).
2. In `backend/.env` (or the host's env vars):
   `DATABASE_URL=postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres`
3. Run `alembic upgrade head` once to create the schema.

## Deploying (Render + Vercel + Supabase)

**Render (API)** — new Web Service from this repo:
- Root directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Env vars: `DATABASE_URL` (Supabase pooler URL), `SECRET_KEY`
  (`python -c "import secrets; print(secrets.token_hex(32))"`)
- Health check path: `/health`

**Vercel (frontend)** — import the repo, root directory `frontend`. Edit
[frontend/vercel.json](frontend/vercel.json) to point the `/api/*` rewrite at
your Render URL; the app then calls the API same-origin, so no CORS setup is
needed.

Note: Render's free tier sleeps after idle, so the first request after a
pause takes ~30–60s.
