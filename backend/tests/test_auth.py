from tests.conftest import register_user


def test_register_returns_token_and_default_categories(anon_client):
    response = anon_client.post(
        "/api/v1/auth/register", json={"email": "new@example.com", "password": "a-secure-pw"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "new@example.com"

    categories = anon_client.get(
        "/api/v1/categories", headers={"Authorization": f"Bearer {body['token']}"}
    ).json()
    names = {c["name"] for c in categories}
    assert {"Salary", "Mortgage", "Groceries", "Credit Card Debt"} <= names


def test_register_duplicate_email_conflicts(anon_client):
    register_user(anon_client, "dup@example.com")
    response = anon_client.post(
        "/api/v1/auth/register", json={"email": "dup@example.com", "password": "a-secure-pw"}
    )
    assert response.status_code == 409


def test_login_and_me_roundtrip(anon_client):
    register_user(anon_client, "tarek@example.com")
    response = anon_client.post(
        "/api/v1/auth/login", json={"email": "tarek@example.com", "password": "a-secure-pw"}
    )
    assert response.status_code == 200
    token = response.json()["token"]

    me = anon_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "tarek@example.com"


def test_login_wrong_password_is_401(anon_client):
    register_user(anon_client, "tarek@example.com")
    response = anon_client.post(
        "/api/v1/auth/login", json={"email": "tarek@example.com", "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_endpoints_require_auth(anon_client):
    assert anon_client.get("/api/v1/categories").status_code == 401
    assert anon_client.get("/api/v1/budgets/2026").status_code == 401
    assert anon_client.get("/api/v1/months/2026/6").status_code == 401
    assert anon_client.get("/api/v1/auth/me").status_code == 401


def test_garbage_token_is_401(anon_client):
    response = anon_client.get(
        "/api/v1/categories", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_users_cannot_see_each_others_data(anon_client):
    alice = {"Authorization": f"Bearer {register_user(anon_client, 'alice@example.com')}"}
    bob = {"Authorization": f"Bearer {register_user(anon_client, 'bob@example.com')}"}

    expense = anon_client.post(
        "/api/v1/expenses",
        json={"spend_date": "2026-06-03", "amount_pence": 1_000, "description": "Alice's"},
        headers=alice,
    ).json()

    bob_expenses = anon_client.get("/api/v1/expenses?year=2026&month=6", headers=bob).json()
    assert bob_expenses == []

    # Bob can't delete Alice's expense, nor edit her budget cells.
    assert (
        anon_client.delete(f"/api/v1/expenses/{expense['id']}", headers=bob).status_code == 404
    )
    alice_groceries = next(
        c
        for c in anon_client.get("/api/v1/categories", headers=alice).json()
        if c["name"] == "Groceries"
    )
    assert (
        anon_client.put(
            f"/api/v1/budgets/2026/6/categories/{alice_groceries['id']}",
            json={"amount_pence": 1},
            headers=bob,
        ).status_code
        == 404
    )
