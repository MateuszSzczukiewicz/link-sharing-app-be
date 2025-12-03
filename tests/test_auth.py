import pytest

from link_sharing_app.db import get_db


def test_register(client, app):
    response = client.post(
        "/auth/register", json={"email": "test@test.com", "password": "strong_password"}
    )
    assert response.status_code == 201
    assert response.get_json() == {"message": "User registered successfully."}

    with app.app_context():
        assert (
            get_db()
            .execute("SELECT * FROM users WHERE email = 'test@test.com'")
            .fetchone()
            is not None
        )


@pytest.mark.parametrize(
    ("email", "password", "message", "status_code"),
    (
        ("", "strong_password", "Email is required.", 400),
        ("test@test.com", "", "Password is required.", 400),
        ("test@test.com", "strong_password", "User is already registered.", 409),
    ),
)
def test_register_validate_input(client, email, password, message, status_code):
    client.post(
        "/auth/register", json={"email": "test@test.com", "password": "strong_password"}
    )
    response = client.post(
        "/auth/register", json={"email": email, "password": password}
    )
    assert response.status_code == status_code
    assert response.get_json()["error"] == message


def test_register_invalid_json_format(client):
    response = client.post(
        "/auth/register", data="Invalid JSON", content_type="application/json"
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid JSON data."


def test_register_invalid_json_header(client):
    response = client.post("/auth/register", data='{"email": "a", "password": "b"}')
    assert response.status_code == 415
    assert response.get_json()["error"] == "Invalid JSON data."


def test_register_missing_email(client):
    response = client.post("/auth/register", json={"password": "strong_password"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Email is required."


def test_register_missing_password(client):
    response = client.post("/auth/register", json={"email": "test@example.com"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Password is required."


def test_login(client, auth):
    register_response = client.post(
        "/auth/register",
        json={"email": "email@gmail.com", "password": "strong_password"},
    )
    assert register_response.status_code == 201

    auth_response = auth.login("email@gmail.com", "strong_password")
    assert auth_response.status_code == 200
    json_data = auth_response.get_json()
    assert json_data["message"] == "User logged in successfully."
    assert "token" in json_data
    assert json_data["token"]


@pytest.mark.parametrize(
    ("email", "password", "message", "status_code"),
    (
        ("bad_email@test.com", "strong_password", "User is not found.", 404),
        ("validate@test.com", "bad_password", "Incorrect password.", 401),
    ),
)
def test_login_validate_input(client, auth, email, password, message, status_code):
    client.post(
        "/auth/register",
        json={"email": "validate@test.com", "password": "strong_password"},
    )
    response = auth.login(email, password)
    assert response.status_code == status_code
    assert response.get_json()["error"] == message


def test_login_invalid_json_format(client):
    response = client.post(
        "/auth/login", data="Invalid JSON", content_type="application/json"
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid JSON data."


def test_login_missing_json_header(client):
    response = client.post("/auth/login", data='{"email": "a", "password": "b"}')
    assert response.status_code == 415
    assert response.get_json()["error"] == "Invalid JSON data."


def test_login_missing_email(client):
    response = client.post("/auth/login", json={"password": "strong_password"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Email is required."


def test_login_missing_password(client):
    response = client.post("/auth/login", json={"email": "test@gmail.com"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Password is required."


def test_login_nonexisten_user(auth):
    response = auth.login("nonexistent@test.pl", "strong_password")
    assert response.status_code == 404
    assert response.get_json()["error"] == "User is not found."


def test_login_incorrect_password(client):
    email = "email@gmail.com"
    client.post(
        "/auth/register",
        json={"email": email, "password": "good_password"},
    )
    response = client.post(
        "/auth/login", json={"email": email, "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "Incorrect password."


def test_login_success(client):
    email = "email@gmail.com"
    password = "strong_password"
    client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "token" in response.get_json()


def test_login_no_secret_key(client, app, monkeypatch):
    client.post(
        "/auth/register",
        json={"email": "test@gmail.com", "password": "strong_password"},
    )
    monkeypatch.delenv("SECRET_KEY", raising=False)
    app.config["SECRET_KEY"] = None
    with pytest.raises(ValueError, match="No secret key set."):
        client.post(
            "/auth/login",
            json={"email": "test@gmail.com", "password": "strong_password"},
        )
