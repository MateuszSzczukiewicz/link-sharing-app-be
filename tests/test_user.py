from flask import jsonify

from link_sharing_app.db import get_db

from .fake_db import FakeConnection


def test_get_user_by_id(client, app):
    response = client.get("/users/1")

    if response is None:
        return jsonify({"error": "User not found."}), 404

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Success.",
        "data": {
            "email": "test@gmail.com",
            "first_name": "Test",
            "last_name": "Testowy",
            "image_url": "https://link_to_image.com",
        },
    }

    with app.app_context():
        assert dict(
            get_db()
            .execute(
                "SELECT email, first_name, last_name, image_url FROM users WHERE id = 1"
            )
            .fetchone()
        ) == {
            "email": "test@gmail.com",
            "first_name": "Test",
            "last_name": "Testowy",
            "image_url": "https://link_to_image.com",
        }
    return None


def test_get_user_by_id_convertion(client):
    response = client.get("/users/1")
    data = response.get_json()

    assert isinstance(data["data"], dict)

    for key in ["email", "first_name", "last_name", "image_url"]:
        assert key in data["data"]


def test_get_user_by_id_not_found(client):
    response = client.get("/users/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found."}


def test_edit_user_by_id(client, app):
    response = client.patch(
        "/users/1", json={"first_name": "Atest", "last_name": "Atestowy"}
    )

    if response is None:
        return jsonify({"error": "User not found."}), 404

    assert response.status_code == 200
    assert response.get_json() == {"message": "User edited successfully."}

    with app.app_context():
        assert dict(
            get_db()
            .execute("SELECT first_name, last_name FROM users WHERE id = 1")
            .fetchone()
        ) == {"first_name": "Atest", "last_name": "Atestowy"}
    return None


def test_edit_user_by_id_without_data(client):
    response = client.patch("/users/1")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid JSON data."}


def test_edit_user_by_id_with_invalid_data(client):
    response = client.patch("/users/1", json={"surname": "Atestowy"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid field."}


def test_edit_user_by_id_integrity_error(client, monkeypatch):
    monkeypatch.setattr("link_sharing_app.users.get_db", lambda: FakeConnection())

    response = client.patch(
        "/users/1", json={"first_name": "NewName", "last_name": "NewLastName"}
    )
    assert response.status_code == 500
    assert response.get_json()["error"] == "Database integrity error"


def test_edit_user_by_id_not_found(client):
    response = client.patch(
        "/users/9999", json={"first_name": "New", "last_name": "User"}
    )
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found."}


def test_delete_user_by_id(client, app):
    response = client.delete("/users/1")

    if response is None:
        return jsonify({"error": "User not found."}), 404

    assert response.status_code == 200
    assert response.get_json() == {"message": "User deleted successfully."}

    with app.app_context():
        assert get_db().execute("SELECT * FROM users WHERE id = 1").fetchone() is None
    return None


def test_delete_user_not_found(client):
    response = client.delete("/users/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found."}


def test_delete_user_by_id_integrity_error(client, monkeypatch):
    monkeypatch.setattr("link_sharing_app.users.get_db", lambda: FakeConnection())

    response = client.delete("/users/1")

    assert response.status_code == 500
    assert response.get_json()["error"] == "Database integrity error"
