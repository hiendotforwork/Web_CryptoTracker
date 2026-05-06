"""
Auth routes module.

Định nghĩa các routes cho authentication:
- POST /api/auth/register: Đăng ký user mới
- POST /api/auth/login: Đăng nhập và nhận JWT token
"""

import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import db, User

# Khởi tạo Blueprint
auth_bp = Blueprint("auth", __name__)


def validate_register_input(data: dict) -> tuple[bool, str]:
    """
    Validate input cho đăng ký.

    Args:
        data: Dictionary chứa username, email, password

    Returns:
        Tuple (is_valid, error_message)
    """
    # Kiểm tra các trường bắt buộc
    required_fields = ["username", "email", "password"]
    for field in required_fields:
        if field not in data or not data.get(field):
            return False, "Vui lòng điền đầy đủ thông tin"

    username = data["username"].strip()
    email = data["email"].strip()
    password = data["password"]

    # Validate username: 3-50 ký tự
    if len(username) < 3 or len(username) > 50:
        return False, "Username phải từ 3 đến 50 ký tự"

    # Validate email: đúng format
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        return False, "Email không đúng định dạng"

    # Validate password: tối thiểu 6 ký tự
    if len(password) < 6:
        return False, "Mật khẩu phải ít nhất 6 ký tự"

    return True, ""


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Route đăng ký user mới.

    Request body:
        - username (str): Tên đăng nhập (3-50 ký tự)
        - email (str): Email hợp lệ
        - password (str): Mật khẩu (ít nhất 6 ký tự)

    Returns:
        HTTP 201: {'message': 'Đăng ký thành công', 'user': {...}}
        HTTP 400: {'error': '...'}
        HTTP 409: {'error': 'Username/Email đã tồn tại'}
    """
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Request body phải là JSON"}), 400

    if not data:
        return jsonify({"error": "Request body phải là JSON"}), 400

    # Validate input
    is_valid, error_msg = validate_register_input(data)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    username = data["username"].strip()
    email = data["email"].strip()
    password = data["password"]

    # Kiểm tra trùng username
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username đã tồn tại"}), 409

    # Kiểm tra trùng email
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email đã tồn tại"}), 409

    # Tạo user mới
    new_user = User(username=username, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Đã có lỗi xảy ra khi lưu user"}), 500

    return jsonify({
        "message": "Đăng ký thành công",
        "user": new_user.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Route đăng nhập.

    Request body:
        - username (str): Tên đăng nhập
        - password (str): Mật khẩu

    Returns:
        HTTP 200: {'access_token': '...', 'user': {...}}
        HTTP 400: {'error': '...'}
        HTTP 401: {'error': 'Sai tên đăng nhập hoặc mật khẩu'}
    """
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Request body phải là JSON"}), 400

    if not data:
        return jsonify({"error": "Request body phải là JSON"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Vui lòng điền username và password"}), 400

    # Tìm user
    user = User.query.filter_by(username=username.strip()).first()

    # Dùng cùng message lỗi để tránh information disclosure
    if not user or not user.check_password(password):
        return jsonify({"error": "Sai tên đăng nhập hoặc mật khẩu"}), 401

    # Tạo JWT token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username
        }
    }), 200