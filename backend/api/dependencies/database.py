"""Request-scoped database session.

One session per request, acting as the unit of work: services/repositories
only flush; the commit happens here once the request handler finishes
without raising. Any exception rolls the whole request back.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from database.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


DbSession = Annotated[Session, Depends(get_db)]
