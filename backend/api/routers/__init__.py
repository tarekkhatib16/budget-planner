from fastapi import APIRouter

from api.routers import budgets, categories, expenses, months

api_router = APIRouter()
api_router.include_router(categories.router)
api_router.include_router(budgets.router)
api_router.include_router(expenses.router)
api_router.include_router(months.router)
