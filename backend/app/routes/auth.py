"""
Auth routes module.

Định nghĩa các routes cho authentication:
- POST /api/auth/register: Đăng ký user mới
- POST /api/auth/login: Đăng nhập và nhận JWT token
- PATCH /api/auth/change-password: Đổi mật khẩu (yêu cầu đăng nhập)
- PATCH /api/auth/change-username: Đổi tên đăng nhập (yêu cầu đăng nhập)
- DELETE /api/auth/delete-account: Xóa tài khoản (yêu cầu đăng nhập)
"""

import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User
from app.limiter import limiter

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
@limiter.limit("3 per minute")
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
@limiter.limit("5 per minute")
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


@auth_bp.route("/change-password", methods=["PATCH"])
@jwt_required()
@limiter.limit("3 per minute")
def change_password():
    """
    Đổi mật khẩu người dùng.

    Yêu cầu JWT token hợp lệ trong header Authorization.

    Request body:
        - current_password (str): Mật khẩu hiện tại để xác nhận danh tính
        - new_password (str): Mật khẩu mới (tối thiểu 6 ký tự)

    Returns:
        HTTP 200: {'message': 'Đổi mật khẩu thành công'}
        HTTP 400: {'error': '...'} — thiếu trường hoặc mật khẩu mới không hợp lệ
        HTTP 401: {'error': '...'} — mật khẩu hiện tại sai
        HTTP 404: {'error': '...'} — user không tồn tại
    """
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Request body phải là JSON"}), 400

    if not data:
        return jsonify({"error": "Request body phải là JSON"}), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"error": "Vui lòng điền đầy đủ mật khẩu hiện tại và mật khẩu mới"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Mật khẩu mới phải ít nhất 6 ký tự"}), 400

    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "Không tìm thấy tài khoản"}), 404

    if not user.check_password(current_password):
        return jsonify({"error": "Mật khẩu hiện tại không đúng"}), 401

    try:
        user.set_password(new_password)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Đã có lỗi xảy ra khi đổi mật khẩu"}), 500

    return jsonify({"message": "Đổi mật khẩu thành công"}), 200


@auth_bp.route("/change-username", methods=["PATCH"])
@jwt_required()
@limiter.limit("3 per minute")
def change_username():
    """
    Đổi tên đăng nhập (username).

    Yêu cầu JWT token hợp lệ trong header Authorization.

    Request body:
        - new_username (str): Username mới (3-50 ký tự)
        - current_password (str): Mật khẩu hiện tại để xác nhận danh tính

    Returns:
        HTTP 200: {'message': '...', 'user': {...}} — trả về user đã cập nhật
        HTTP 400: {'error': '...'} — thiếu trường hoặc username không hợp lệ
        HTTP 401: {'error': '...'} — mật khẩu xác nhận sai
        HTTP 404: {'error': '...'} — user không tồn tại
        HTTP 409: {'error': '...'} — username đã tồn tại
    """
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Request body phải là JSON"}), 400

    if not data:
        return jsonify({"error": "Request body phải là JSON"}), 400

    new_username = data.get("new_username", "").strip()
    current_password = data.get("current_password")

    if not new_username or not current_password:
        return jsonify({"error": "Vui lòng điền đầy đủ username mới và mật khẩu xác nhận"}), 400

    if len(new_username) < 3 or len(new_username) > 50:
        return jsonify({"error": "Username phải từ 3 đến 50 ký tự"}), 400

    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "Không tìm thấy tài khoản"}), 404

    if not user.check_password(current_password):
        return jsonify({"error": "Mật khẩu xác nhận không đúng"}), 401

    if new_username == user.username:
        return jsonify({"error": "Username mới phải khác username hiện tại"}), 400

    if User.query.filter_by(username=new_username).first():
        return jsonify({"error": "Username này đã được sử dụng"}), 409

    try:
        user.username = new_username
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Đã có lỗi xảy ra khi đổi username"}), 500

    return jsonify({
        "message": "Đổi username thành công",
        "user": user.to_dict()
    }), 200


@auth_bp.route("/delete-account", methods=["DELETE"])
@jwt_required()
@limiter.limit("3 per minute")
def delete_account():
    """
    Xóa tài khoản người dùng.

    Yêu cầu JWT token hợp lệ trong header Authorization.
    Xóa user sẽ tự động xóa cascade tất cả dữ liệu watchlist liên quan.

    Request body:
        - current_password (str): Mật khẩu để xác nhận danh tính trước khi xóa

    Returns:
        HTTP 200: {'message': 'Tài khoản đã được xóa thành công'}
        HTTP 400: {'error': '...'} — thiếu mật khẩu xác nhận
        HTTP 401: {'error': '...'} — mật khẩu xác nhận sai
        HTTP 404: {'error': '...'} — user không tồn tại
    """
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Request body phải là JSON"}), 400

    if not data:
        return jsonify({"error": "Request body phải là JSON"}), 400

    current_password = data.get("current_password")

    if not current_password:
        return jsonify({"error": "Vui lòng nhập mật khẩu để xác nhận xóa tài khoản"}), 400

    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "Không tìm thấy tài khoản"}), 404

    if not user.check_password(current_password):
        return jsonify({"error": "Mật khẩu xác nhận không đúng"}), 401

    try:
        # cascade="all, delete-orphan" trên watchlist_items sẽ tự xóa watchlist
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Đã có lỗi xảy ra khi xóa tài khoản"}), 500

    return jsonify({"message": "Tài khoản đã được xóa thành công"}), 200