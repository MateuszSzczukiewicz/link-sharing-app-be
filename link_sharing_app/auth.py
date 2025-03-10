import datetime
import jwt
import os
from dotenv import load_dotenv
from flask import (
    Blueprint,
    jsonify,
    request,
)
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db

load_dotenv()

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    db = get_db()

    if not email:
        return jsonify({"error": "email is required"}), 400
    elif not password:
        return jsonify({"error": "email is required"}), 400

    try:
        db.execute(
            "INSERT INTO user (email, password) VALUES (?, ?)",
            (email, generate_password_hash(password)),
        )
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except db.IntegrityError:
        return jsonify({"error": "User is already registered."}), 409


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    db = get_db()

    secret_key = os.getenv("secret_key")
    if not secret_key:
        raise ValueError("No secret key set.")

    if not email:
        return jsonify({"error": "email is required"}), 400
    elif not password:
        return jsonify({"error": "email is required"}), 400

    user = db.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()

    if user is None:
        return jsonify({"error": "User is not found."}), 404
    elif not check_password_hash(user["password"], password):
        return jsonify({"error": "Incorrect password."}), 401

    payload_data = {
        "user_id": user["id"],
        "exp": datetime.datetime.now() + datetime.timedelta(hours=24),
    }

    token = jwt.encode(payload=payload_data, key=secret_key)

    return jsonify({"message": "User logged in successfully", "token": token}), 200
