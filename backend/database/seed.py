"""Seed the default categories from the original spreadsheet.

Idempotent: existing categories are left untouched. Run from backend/:

    .venv/bin/python -m database.seed
"""

from api.models import Category
from api.repositories.category_repository import CategoryRepository
from api.shared.enums import CategoryGroup
from database.session import SessionLocal

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


def seed() -> None:
    with SessionLocal() as session:
        repo = CategoryRepository(session)
        created = 0
        for group, names in DEFAULT_CATEGORIES:
            for sort_order, name in enumerate(names):
                if repo.find_by_name(name, group) is None:
                    repo.add(Category(name=name, group=group, sort_order=sort_order))
                    created += 1
        session.commit()
        print(f"Seeded {created} categories")


if __name__ == "__main__":
    seed()
