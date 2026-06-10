"""Declarative base shared by all ORM models and Alembic."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
