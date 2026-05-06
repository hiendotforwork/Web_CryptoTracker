"""
Watchlist routes module.

Định nghĩa các routes cho watchlist:
- GET /api/watchlist/: Lấy danh sách watchlist của user
- POST /api/watchlist/: Thêm coin vào watchlist
- DELETE /api/watchlist/<coin_id>: Xóa coin khỏi watchlist

Tất cả endpoints đều cần JWT token.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Watchlist, Coin
from sqlalchemy.exc import IntegrityError

# Khởi tạo Blueprint
watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/", methods=["GET"])
@jwt_required()
def get_watchlist():
    """
    Lấy danh sách watchlist của user hiện tại.

    Returns:
        HTTP 200: {'watchlist': [...]}
    """
    user_id = get_jwt_identity()
    user_id = int(user_id)

    watchlist_items = Watchlist.query.filter_by(user_id=user_id).all()

    return jsonify({
        "watchlist": [item.to_dict() for item in watchlist_items]
    })


@watchlist_bp.route("/", methods=["POST"])
@jwt_required()
def add_to_watchlist():
    """
    Thêm coin vào watchlist.

    Request body:
        - coin_id (str): ID của coin

    Returns:
        HTTP 201: {'message': 'Đã thêm vào watchlist', 'item': {...}}
        HTTP 400: {'error': '...'}
        HTTP 404: {'error': 'Coin không tồn tại'}
        HTTP 409: {'error': 'Coin đã có trong watchlist'}
    """
    user_id = int(get_jwt_identity())

    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Request body phải là JSON"}), 400

    if not data or "coin_id" not in data:
        return jsonify({"error": "Vui lòng cung cấp coin_id"}), 400

    coin_id = data["coin_id"]

    # Kiểm tra coin tồn tại
    coin = Coin.query.get(coin_id)
    if not coin:
        return jsonify({"error": f"Coin {coin_id} không tồn tại trong hệ thống"}), 404

    # Thêm vào watchlist
    new_item = Watchlist(user_id=user_id, coin_id=coin_id)

    try:
        db.session.add(new_item)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Coin đã có trong watchlist"}), 409

    return jsonify({
        "message": "Đã thêm vào watchlist",
        "item": new_item.to_dict()
    }), 201


@watchlist_bp.route("/<coin_id>", methods=["DELETE"])
@jwt_required()
def remove_from_watchlist(coin_id: str):
    """
    Xóa coin khỏi watchlist.

    Args:
        coin_id: ID của coin cần xóa

    Returns:
        HTTP 200: {'message': 'Đã xóa ... khỏi watchlist'}
        HTTP 404: {'error': 'Coin không có trong watchlist của bạn'}
    """
    user_id = int(get_jwt_identity())

    # Tìm và xóa (chỉ xóa nếu thuộc về user hiện tại)
    item = Watchlist.query.filter_by(
        user_id=user_id,
        coin_id=coin_id
    ).first()

    if not item:
        return jsonify({"error": f"Coin {coin_id} không có trong watchlist của bạn"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        "message": f"Đã xóa {coin_id} khỏi watchlist"
    })