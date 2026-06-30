"""Builds the service layer for each request.

Data services require CurrentUser, which both protects every route that
uses them and scopes all queries to the authenticated user.
"""

from typing import Annotated

from fastapi import Depends

from api.core.config import get_settings
from api.dependencies.auth import CurrentUser
from api.dependencies.database import DbSession
from api.repositories.budget_repository import BudgetRepository
from api.repositories.category_repository import CategoryRepository
from api.repositories.expense_repository import ExpenseRepository
from api.repositories.user_repository import UserRepository
from api.services.auth_service import AuthService
from api.services.budget_service import BudgetService
from api.services.category_service import CategoryService
from api.services.expense_service import ExpenseService
from api.services.month_service import MonthService


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(UserRepository(db), CategoryRepository(db), get_settings())


def get_category_service(db: DbSession, user: CurrentUser) -> CategoryService:
    return CategoryService(CategoryRepository(db), user.id)


def get_budget_service(db: DbSession, user: CurrentUser) -> BudgetService:
    return BudgetService(
        CategoryRepository(db), BudgetRepository(db), ExpenseRepository(db), user.id
    )


def get_expense_service(db: DbSession, user: CurrentUser) -> ExpenseService:
    return ExpenseService(ExpenseRepository(db), user.id)


def get_month_service(db: DbSession, user: CurrentUser) -> MonthService:
    return MonthService(
        CategoryRepository(db), BudgetRepository(db), ExpenseRepository(db), user.id
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
BudgetServiceDep = Annotated[BudgetService, Depends(get_budget_service)]
ExpenseServiceDep = Annotated[ExpenseService, Depends(get_expense_service)]
MonthServiceDep = Annotated[MonthService, Depends(get_month_service)]
