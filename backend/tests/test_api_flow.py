"""End-to-end flow through the HTTP API: categories -> budget -> expenses -> views."""


def _create_category(client, name, group, sort_order=0):
    response = client.post(
        "/api/v1/categories",
        json={"name": name, "group": group, "sort_order": sort_order},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_duplicate_category_in_same_group_conflicts(client):
    _create_category(client, "Groceries", "spending")
    response = client.post(
        "/api/v1/categories", json={"name": "Groceries", "group": "spending"}
    )
    assert response.status_code == 409


def test_year_view_computes_group_totals_and_savings(client):
    salary = _create_category(client, "Salary", "income")
    mortgage = _create_category(client, "Mortgage", "bills")
    groceries = _create_category(client, "Groceries", "spending")

    for category, amount in [(salary, 412_000), (mortgage, 198_300), (groceries, 40_000)]:
        response = client.put(
            f"/api/v1/budgets/2026/6/categories/{category['id']}",
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
    groceries = _create_category(client, "Groceries", "spending")
    client.put(
        f"/api/v1/budgets/2026/6/categories/{groceries['id']}",
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
    groceries = _create_category(client, "Groceries", "spending")
    url = f"/api/v1/budgets/2026/6/categories/{groceries['id']}"
    client.put(url, json={"amount_pence": 10_000})
    client.put(url, json={"amount_pence": 25_000})

    view = client.get("/api/v1/budgets/2026").json()
    spending = next(s for s in view["sections"] if s["group"] == "spending")
    assert spending["rows"][0]["amounts_pence"][5] == 25_000


def test_missing_resources_return_404(client):
    assert client.delete("/api/v1/expenses/999").status_code == 404
    assert (
        client.put(
            "/api/v1/budgets/2026/6/categories/999", json={"amount_pence": 1}
        ).status_code
        == 404
    )
