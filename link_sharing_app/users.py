from flask import Blueprint, jsonify, request

from .db import get_db

bp = Blueprint("users", __name__, url_prefix="/users")


def get_user(id):
    db = get_db()
    return db.execute(
        "SELECT email, first_name, last_name, image_url FROM users WHERE id = ?",
        (id,),
    ).fetchone()


@bp.route("/<int:id>", methods=["GET"])
def get_user_by_id(id):
    user = get_user(id)

    if user is None:
        return jsonify({"error": "User not found."}), 404

    return jsonify({"data": dict(user), "message": "Success."}), 200


@bp.route("/<int:id>", methods=["PATCH"])
def edit_user_by_id(id):
    db = get_db()
    user = get_user(id)

    if user is None:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON data."}), 400

    allowed_fields = {"email", "password", "first_name", "last_name", "image_url"}

    for field in data:
        if field not in allowed_fields:
            return jsonify({"error": "Invalid field."}), 400

    set_clause = ", ".join([f"{field} = ?" for field in data])
    values = list(data.values())

    try:
        db.execute(
            f"UPDATE users SET {set_clause} WHERE id = ?",
            (tuple(values) + (id,)),
        )
        db.commit()

        return jsonify({"message": "User edited successfully."}), 200
    except db.IntegrityError:
        return jsonify({"error": "Database integrity error"}), 500


@bp.route("/<int:id>", methods=["DELETE"])
def delete_user_by_id(id):
    db = get_db()
    user = get_user(id)

    if user is None:
        return jsonify({"error": "User not found."}), 404

    try:
        db.execute(
            "DELETE FROM users WHERE id = ?",
            (id,),
        )
        db.commit()

        return jsonify({"message": "User deleted successfully."}), 200
    except db.IntegrityError:
        return jsonify({"error": "Database integrity error"}), 500
