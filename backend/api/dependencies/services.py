"""Builds the service layer for each request.

Routers depend on these providers instead of constructing services
themselves, so swapping an implementation (or overriding in tests) is a
one-line change.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from api.dependencies.database import get_db
from api.repositories.budget_repository import BudgetRepository
from api.repositories.category_repository import CategoryRepository
from api.repositories.expense_repository import ExpenseRepository
from api.services.budget_service import BudgetService
from api.services.category_service import CategoryService
from api.services.expense_service import ExpenseService
from api.services.month_service import MonthService

DbSession = Annotated[Session, Depends(get_db)]


def get_category_service(db: DbSession) -> CategoryService:
    return CategoryService(CategoryRepository(db))


def get_budget_service(db: DbSession) -> BudgetService:
    return BudgetService(CategoryRepository(db), BudgetRepository(db))


def get_expense_service(db: DbSession) -> ExpenseService:
    return ExpenseService(ExpenseRepository(db))


def get_month_service(db: DbSession) -> MonthService:
    return MonthService(CategoryRepository(db), BudgetRepository(db), ExpenseRepository(db))


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
BudgetServiceDep = Annotated[BudgetService, Depends(get_budget_service)]
ExpenseServiceDep = Annotated[ExpenseService, Depends(get_expense_service)]
MonthServiceDep = Annotated[MonthService, Depends(get_month_service)]
