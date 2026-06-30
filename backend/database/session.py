"""Engine and session factory.

SQLite needs `check_same_thread=False` because FastAPI may service a request
on a different thread than the one that opened the connection.

SQLite also doesn't enforce foreign keys unless you tell it to per
connection (`PRAGMA foreign_keys=ON`). Without this, ON DELETE CASCADE /
SET NULL clauses are silently ignored — which would diverge from Postgres
behaviour in production.
"""

import sqlite3

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from api.core.config import get_settings

settings = get_settings()

_connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

# pool_pre_ping checks connections before use — remote Postgres (e.g.
# Supabase's pooler) silently drops idle connections, and without this the
# first request after an idle period would fail.
engine = create_engine(settings.database_url, connect_args=_connect_args, pool_pre_ping=True)


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    # Inspect the dbapi connection directly so this applies to any
    # SQLite engine (the app's and tests') and is a no-op on Postgres.
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
