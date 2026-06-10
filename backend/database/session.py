"""Engine and session factory.

SQLite needs `check_same_thread=False` because FastAPI may service a request
on a different thread than the one that opened the connection.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.core.config import get_settings

settings = get_settings()

_connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, connect_args=_connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
