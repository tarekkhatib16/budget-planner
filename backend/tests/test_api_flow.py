"""End-to-end flow through the HTTP API as an authenticated user.

The `client` fixture is a freshly registered account, so the default
spreadsheet categories (Salary, Groceries, ...) already exist.
"""


def _category_id(client, name):
    categories = client.get("/api/v1/categories").json()
    return next(c["id"] for c in categories if c["name"] == name)


def test_duplicate_category_in_same_group_conflicts(client):
    response = client.post(
        "/api/v1/categories", json={"name": "Groceries", "group": "spending"}
    )
    assert response.status_code == 409


def test_create_category_in_new_group_succeeds(client):
    response = client.post(
        "/api/v1/categories", json={"name": "Coffee Fund", "group": "spending"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Coffee Fund"


def test_year_view_computes_group_totals_and_savings(client):
    cells = [("Salary", 412_000), ("Mortgage", 198_300), ("Groceries", 40_000)]
    for name, amount in cells:
        response = client.put(
            f"/api/v1/budgets/2026/6/categories/{_category_id(client, name)}",
            json={"amount_pence": amount},
        )
        assert response.status_code == 200, response.text

    view = client.get("/api/v1/budgets/2026").json()
    totals = {section["group"]: section["totals_pence"] for section in view["sections"]}
    june = 5  # index 5 = June
    assert totals["income"][june] == 412_000
    assert totals["bills"][june] == 198_300
    assert totals["spending"][june] == 40_000
    assert view["monthly_savings_pence"][june] == 412_000 - 198_300 - 40_000
    # Savings accumulate: July has no data, so cumulative stays flat.
    assert view["cumulative_savings_pence"][june + 1] == view["monthly_savings_pence"][june]


def test_month_summary_spreads_budget_and_buckets_expenses(client):
    client.put(
        f"/api/v1/budgets/2026/6/categories/{_category_id(client, 'Groceries')}",
        json={"amount_pence": 80_000},
    )

    response = client.post(
        "/api/v1/expenses",
        json={"spend_date": "2026-06-03", "amount_pence": 1_250, "description": "Lunch"},
    )
    assert response.status_code == 201

    summary = client.get("/api/v1/months/2026/6").json()
    assert summary["spending_budget_pence"] == 80_000
    assert len(summary["weeks"]) == 5
    assert sum(week["allowance_pence"] for week in summary["weeks"]) == 80_000

    week_one = summary["weeks"][0]
    assert week_one["spent_pence"] == 1_250
    assert week_one["saved_pence"] == week_one["allowance_pence"] - 1_250
    assert week_one["expenses"][0]["description"] == "Lunch"
    assert summary["total_saved_pence"] == 80_000 - 1_250


def test_updating_a_budget_cell_overwrites_it(client):
    groceries_id = _category_id(client, "Groceries")
    url = f"/api/v1/budgets/2026/6/categories/{groceries_id}"
    client.put(url, json={"amount_pence": 10_000})
    client.put(url, json={"amount_pence": 25_000})

    view = client.get("/api/v1/budgets/2026").json()
    spending = next(s for s in view["sections"] if s["group"] == "spending")
    groceries_row = next(r for r in spending["rows"] if r["category_id"] == groceries_id)
    assert groceries_row["amounts_pence"][5] == 25_000


def test_copy_forward_replicates_month_across_rest_of_year(client):
    groceries = _category_id(client, "Groceries")
    salary = _category_id(client, "Salary")
    client.put(f"/api/v1/budgets/2026/6/categories/{groceries}", json={"amount_pence": 40_000})
    client.put(f"/api/v1/budgets/2026/6/categories/{salary}", json={"amount_pence": 412_000})
    # A pre-existing later value must be overwritten, not merged around.
    client.put(f"/api/v1/budgets/2026/9/categories/{groceries}", json={"amount_pence": 99_999})

    response = client.post("/api/v1/budgets/2026/6/copy-forward")
    assert response.status_code == 200
    assert response.json()["months_filled"] == 6

    view = client.get("/api/v1/budgets/2026").json()
    spending = next(s for s in view["sections"] if s["group"] == "spending")
    groceries_row = next(r for r in spending["rows"] if r["category_id"] == groceries)
    assert groceries_row["amounts_pence"][5:] == [40_000] * 7  # Jun..Dec all match June
    assert groceries_row["amounts_pence"][:5] == [0] * 5  # Jan..May untouched
    income = next(s for s in view["sections"] if s["group"] == "income")
    salary_row = next(r for r in income["rows"] if r["category_id"] == salary)
    assert salary_row["amounts_pence"][11] == 412_000


def test_copy_forward_from_december_fills_nothing(client):
    response = client.post("/api/v1/budgets/2026/12/copy-forward")
    assert response.status_code == 200
    assert response.json()["months_filled"] == 0


def test_unusual_expenses_are_separate_from_tracker(client):
    # Set a small spending budget so weekly allowances are non-zero.
    client.put(
        f"/api/v1/budgets/2026/6/categories/{_category_id(client, 'Groceries')}",
        json={"amount_pence": 80_000},
    )
    client.post(
        "/api/v1/expenses",
        json={"spend_date": "2026-06-03", "amount_pence": 1_250, "description": "Lunch"},
    )
    client.post(
        "/api/v1/expenses",
        json={
            "spend_date": "2026-06-10",
            "amount_pence": 50_000,
            "description": "Flights",
            "kind": "unusual",
        },
    )

    # The tracker only sees regular expenses.
    summary = client.get("/api/v1/months/2026/6").json()
    assert summary["total_spent_pence"] == 1_250
    assert summary["weeks"][1]["expenses"] == []  # week 2 has only an unusual

    # The expenses endpoint defaults to regular and can be filtered to unusual.
    regulars = client.get("/api/v1/expenses?year=2026&month=6").json()
    assert [e["description"] for e in regulars] == ["Lunch"]
    unusuals = client.get("/api/v1/expenses?year=2026&month=6&kind=unusual").json()
    assert [e["description"] for e in unusuals] == ["Flights"]


def test_year_view_reports_actual_unusual_per_month_and_subtracts_from_savings(client):
    client.put(
        f"/api/v1/budgets/2026/6/categories/{_category_id(client, 'Salary')}",
        json={"amount_pence": 412_000},
    )
    client.post(
        "/api/v1/expenses",
        json={
            "spend_date": "2026-06-10",
            "amount_pence": 50_000,
            "description": "Flights",
            "kind": "unusual",
        },
    )

    view = client.get("/api/v1/budgets/2026").json()
    # The Holiday section is gone from the editable grid.
    assert "holiday" not in {section["group"] for section in view["sections"]}
    # June (index 5) shows the £500 actual unusual spend.
    assert view["monthly_unusual_pence"][5] == 50_000
    # Savings = 412_000 income - 50_000 unusual = 362_000.
    assert view["monthly_savings_pence"][5] == 412_000 - 50_000


def test_overspending_reflects_actual_spend_above_budget(client):
    client.put(
        f"/api/v1/budgets/2026/6/categories/{_category_id(client, 'Salary')}",
        json={"amount_pence": 200_000},
    )
    client.put(
        f"/api/v1/budgets/2026/6/categories/{_category_id(client, 'Groceries')}",
        json={"amount_pence": 50_000},
    )
    # Total regular spend in June: £581. Budget: £500. Overspend: £81.
    for amount in (40_000, 18_100):
        client.post(
            "/api/v1/expenses",
            json={"spend_date": "2026-06-05", "amount_pence": amount},
        )

    view = client.get("/api/v1/budgets/2026").json()
    assert view["monthly_overspending_pence"][5] == 8_100
    # July had no spending so no overspending either.
    assert view["monthly_overspending_pence"][6] == 0
    # Savings: 200_000 (income) - 50_000 (spending budget) - 8_100 (overspend)
    #        = 141_900.
    assert view["monthly_savings_pence"][5] == 141_900


def test_underspending_does_not_create_overspending(client):
    client.put(
        f"/api/v1/budgets/2026/6/categories/{_category_id(client, 'Groceries')}",
        json={"amount_pence": 50_000},
    )
    client.post(
        "/api/v1/expenses",
        json={"spend_date": "2026-06-05", "amount_pence": 10_000},
    )

    view = client.get("/api/v1/budgets/2026").json()
    assert view["monthly_overspending_pence"][5] == 0


def test_month_summary_breaks_down_spending_by_category(client):
    groceries_id = _category_id(client, "Groceries")
    eating_out_id = _category_id(client, "Eating Out")
    client.post(
        "/api/v1/expenses",
        json={"spend_date": "2026-06-05", "amount_pence": 4_000, "category_id": groceries_id},
    )
    client.post(
        "/api/v1/expenses",
        json={"spend_date": "2026-06-05", "amount_pence": 1_500, "category_id": eating_out_id},
    )
    client.post(
        "/api/v1/expenses",
        json={"spend_date": "2026-06-05", "amount_pence": 800},  # uncategorised
    )

    summary = client.get("/api/v1/months/2026/6").json()
    breakdown = {item["name"]: item["amount_pence"] for item in summary["category_breakdown"]}
    assert breakdown["Groceries"] == 4_000
    assert breakdown["Eating Out"] == 1_500
    assert breakdown["Uncategorised"] == 800
    # Categories with zero spend still appear (so the UI gets stable colours);
    # only uncategorised is conditional.
    assert breakdown["Haircut"] == 0


def test_categorising_into_non_spending_group_is_rejected(client):
    salary_id = _category_id(client, "Salary")
    response = client.post(
        "/api/v1/expenses",
        json={"spend_date": "2026-06-05", "amount_pence": 1_000, "category_id": salary_id},
    )
    assert response.status_code == 400
    assert "Spending" in response.json()["detail"]


def test_unknown_category_id_returns_404(client):
    response = client.post(
        "/api/v1/expenses",
        json={"spend_date": "2026-06-05", "amount_pence": 1_000, "category_id": 99999},
    )
    assert response.status_code == 404


def test_deleting_a_category_keeps_its_past_expenses_as_uncategorised(client):
    haircut_id = _category_id(client, "Haircut")
    client.post(
        "/api/v1/expenses",
        json={"spend_date": "2026-06-05", "amount_pence": 2_500, "category_id": haircut_id},
    )
    assert client.delete(f"/api/v1/categories/{haircut_id}").status_code == 204

    summary = client.get("/api/v1/months/2026/6").json()
    breakdown = {item["name"]: item["amount_pence"] for item in summary["category_breakdown"]}
    # The Haircut row is gone but the £25 expense survives as uncategorised.
    assert "Haircut" not in breakdown
    assert breakdown["Uncategorised"] == 2_500


def test_missing_resources_return_404(client):
    assert client.delete("/api/v1/expenses/999").status_code == 404
    assert (
        client.put(
            "/api/v1/budgets/2026/6/categories/999", json={"amount_pence": 1}
        ).status_code
        == 404
    )
