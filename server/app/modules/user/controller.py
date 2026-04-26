from flask import Blueprint, jsonify
from app.modules.user.service import UserService

user_bp = Blueprint("user", __name__)


@user_bp.route("/")
def get_hello():
    return "Hello flask"


@user_bp.route("/users")
def get_users():
    users = UserService.get_users()
    return jsonify([u.name for u in users])
