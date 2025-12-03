from flask import Blueprint, jsonify, request

from .db import get_db
from .users import get_user

bp = Blueprint("links", __name__, url_prefix="/links")


def get_link(id):
    db = get_db()
    return db.execute(
        "SELECT * FROM links WHERE id = ?",
        (id,),
    ).fetchone()


@bp.route("/<int:user_id>", methods=["GET"])
def get_all_links(user_id):
    user = get_user(user_id)
    db = get_db()

    if user is None:
        return jsonify({"error": "User not found."}), 404

    links = db.execute(
        "SELECT * FROM links WHERE user_id = ? ORDER BY created DESC",
        (user_id,),
    ).fetchall()

    return jsonify({"data": [dict(row) for row in links], "message": "Success."}), 200


@bp.route("/", methods=["POST"])
def create_link():
    if not request.is_json:
        return jsonify({"error": "Invalid JSON data."}), 415

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON data."}), 400

    user_id = data.get("user_id")
    platform = data.get("platform")
    url = data.get("url")
    db = get_db()

    if not user_id:
        return jsonify({"error": "User_id is required."}), 400
    if not platform:
        return jsonify({"error": "Platform is required."}), 400
    if not url:
        return jsonify({"error": "Url is required."}), 400

    try:
        db.execute(
            "INSERT INTO links (user_id, platform, url) VALUES (?, ?, ?)",
            (user_id, platform, url),
        )
        db.commit()
        return jsonify({"message": "Link created successfully."}), 201
    except db.IntegrityError:
        return jsonify({"error": "Failed to create link."}), 409


@bp.route("/<int:id>", methods=["PATCH"])
def edit_link_by_id(id):
    db = get_db()
    link = get_link(id)

    if link is None:
        return jsonify({"error": "Link not found."}), 404

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON data."}), 400

    allowed_fields = {"platform", "url"}

    for field in data:
        if field not in allowed_fields:
            return jsonify({"error": "Invalid field."}), 400

    set_clause = ", ".join([f"{field} = ?" for field in data])
    values = list(data.values())

    try:
        db.execute(
            f"UPDATE links SET {set_clause} WHERE id = ?",
            tuple(values) + (id,),
        )
        db.commit()

        return jsonify({"message": "Link edited successfully."}), 200
    except db.IntegrityError:
        return jsonify({"error": "Database integrity error"}), 500


@bp.route("/<int:id>", methods=["DELETE"])
def delete_link_by_id(id):
    db = get_db()
    link = get_link(id)

    if link is None:
        return jsonify({"error": "Link not found."}), 404

    try:
        db.execute("DELETE FROM links where id = ?", (id,))
        db.commit()

        return jsonify({"message": "Link deleted successfully."}), 200
    except db.IntegrityError:
        return jsonify({"error": "Database integrity error"}), 500
