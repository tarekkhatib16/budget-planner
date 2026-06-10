"""The starter categories every new account gets, from the original spreadsheet."""

from api.models import Category
from api.repositories.category_repository import CategoryRepository
from api.shared.enums import CategoryGroup

DEFAULT_CATEGORIES: list[tuple[CategoryGroup, list[str]]] = [
    (CategoryGroup.INCOME, ["Salary", "Bonus"]),
    (
        CategoryGroup.BILLS,
        [
            "Mortgage",
            "Water",
            "Utilities",
            "Council Tax",
            "Phone",
            "Credit Card",
            "Gym",
            "Wifi",
            "Bike",
        ],
    ),
    (
        CategoryGroup.SPENDING,
        ["Groceries", "Eating Out", "Haircut", "Clothing Spend", "Home Spend", "Transport"],
    ),
    (CategoryGroup.HOLIDAY, ["Accommodation", "Flights/Transportation", "Other Spending"]),
    (CategoryGroup.DEBT, ["Credit Card Debt"]),
]


def create_default_categories(repo: CategoryRepository, user_id: int) -> None:
    for group, names in DEFAULT_CATEGORIES:
        for sort_order, name in enumerate(names):
            repo.add(Category(user_id=user_id, name=name, group=group, sort_order=sort_order))
