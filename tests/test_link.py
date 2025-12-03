from link_sharing_app.db import get_db

from .fake_db import FakeConnection


def test_get_all_links_success(client):
    response = client.get("/links/1")
    assert response.status_code == 200

    data = response.get_json()
    assert "data" in data
    assert "message" in data
    assert data["message"] == "Success."
    assert isinstance(data["data"], list)


def test_get_all_links_user_not_found(client):
    response = client.get("/links/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"error": "User not found."}


def test_create_link_success(client, app):
    new_link_data = {
        "user_id": 1,
        "platform": "Twitter",
        "url": "https://twitter.com/some_profile",
    }
    response = client.post("/links/", json=new_link_data)
    assert response.status_code == 201

    data = response.get_json()
    assert data == {"message": "Link created successfully."}

    with app.app_context():
        db = get_db()
        link_in_db = dict(
            db.execute(
                "SELECT user_id, platform, url FROM links WHERE user_id = ? AND platform = ? AND url = ?",
                (1, "Twitter", "https://twitter.com/some_profile"),
            ).fetchone()
        )
        assert link_in_db["user_id"] == 1
        assert link_in_db["platform"] == "Twitter"
        assert link_in_db["url"] == "https://twitter.com/some_profile"


def test_create_link_no_json(client):
    response = client.post("/links/")
    assert response.status_code == 415
    data = response.get_json()
    assert data == {"error": "Invalid JSON data."}


def test_create_link_empty_json(client):
    response = client.post("/links/", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data == {"error": "Invalid JSON data."}


def test_create_link_missing_user_id(client):
    response = client.post(
        "/links/",
        json={"platform": "Twitter", "url": "https://twitter.com/some_profile"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data == {"error": "User_id is required."}


def test_create_link_missing_platform(client):
    response = client.post(
        "/links/", json={"user_id": 1, "url": "https://twitter.com/some_profile"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data == {"error": "Platform is required."}


def test_create_link_missing_url(client):
    response = client.post("/links/", json={"user_id": 1, "platform": "Twitter"})
    assert response.status_code == 400
    data = response.get_json()
    assert data == {"error": "Url is required."}


def test_create_link_integrity_error(client, monkeypatch):
    monkeypatch.setattr("link_sharing_app.links.get_db", lambda: FakeConnection())

    response = client.post(
        "/links/",
        json={
            "user_id": 1,
            "platform": "Twitter",
            "url": "https://twitter.com/some_profile",
        },
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Failed to create link."


def test_edit_link_by_id_success(client, app):
    response = client.patch(
        "/links/1",
        json={"platform": "LinkedIn", "url": "https://linked.in/new_profile"},
    )
    assert response.status_code == 200

    data = response.get_json()
    assert data == {"message": "Link edited successfully."}

    with app.app_context():
        db = get_db()
        link_in_db = dict(
            db.execute("SELECT platform, url FROM links WHERE id = 1").fetchone()
        )
        assert link_in_db["platform"] == "LinkedIn"
        assert link_in_db["url"] == "https://linked.in/new_profile"


def test_edit_link_by_id_not_found(client):
    response = client.patch("/links/9999", json={"platform": "Twitter"})
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"error": "Link not found."}


def test_edit_link_by_id_no_json(client):
    response = client.patch("/links/1")
    assert response.status_code == 400
    data = response.get_json()
    assert data == {"error": "Invalid JSON data."}


def test_edit_link_by_id_invalid_field(client):
    response = client.patch("/links/1", json={"user_id": 10})
    assert response.status_code == 400
    data = response.get_json()
    assert data == {"error": "Invalid field."}


def test_edit_link_by_id_integrity_error(client, monkeypatch):
    monkeypatch.setattr("link_sharing_app.links.get_db", lambda: FakeConnection())

    response = client.patch("/links/1", json={"platform": "Twitter", "url": "any"})
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Database integrity error"


def test_delete_link_by_id_success(client, app):
    response = client.delete("/links/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"message": "Link deleted successfully."}

    with app.app_context():
        db = get_db()
        link_in_db = db.execute("SELECT * FROM links WHERE id = 1").fetchone()
        assert link_in_db is None


def test_delete_link_by_id_not_found(client):
    response = client.delete("/links/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"error": "Link not found."}


def test_delete_link_by_id_integrity_error(client, monkeypatch):
    monkeypatch.setattr("link_sharing_app.links.get_db", lambda: FakeConnection())

    response = client.delete("/links/1")
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Database integrity error"
