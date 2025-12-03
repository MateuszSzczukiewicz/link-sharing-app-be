import datetime
import os

import jwt
from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

load_dotenv()

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({"error": "Invalid JSON data."}), 415

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON data."}), 400

    email = data.get("email")
    password = data.get("password")
    db = get_db()

    if not email:
        return jsonify({"error": "Email is required."}), 400
    if not password:
        return jsonify({"error": "Password is required."}), 400

    try:
        db.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, generate_password_hash(password)),
        )
        db.commit()
        return jsonify({"message": "User registered successfully."}), 201
    except db.IntegrityError:
        return jsonify({"error": "User is already registered."}), 409


@bp.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "Invalid JSON data."}), 415
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON data."}), 400

    email = data.get("email")
    password = data.get("password")
    db = get_db()

    secret_key = current_app.config.get("SECRET_KEY") or os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("No secret key set.")

    if not email:
        return jsonify({"error": "Email is required."}), 400
    if not password:
        return jsonify({"error": "Password is required."}), 400

    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if user is None:
        return jsonify({"error": "User is not found."}), 404
    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Incorrect password."}), 401

    payload_data = {
        "user_id": user["id"],
        "exp": datetime.datetime.now() + datetime.timedelta(hours=24),
    }

    token = jwt.encode(payload=payload_data, key=secret_key)

    return jsonify({"message": "User logged in successfully.", "token": token}), 200
