"""
News routes module.

Định nghĩa các routes cho news:
- GET /api/news/: Danh sách tin tức có phân trang
- POST /api/news/fetch: Trigger fetch thủ công (development only)
"""

from flask import Blueprint, request, jsonify, current_app
from app.models import db, News

# Khởi tạo Blueprint
news_bp = Blueprint("news", __name__)

# Cấu hình phân trang mặc định
NEWS_PER_PAGE = 20


@news_bp.route("/", methods=["GET"], strict_slashes=False)
def get_news():
    """
    Lấy danh sách tin tức có phân trang.

    Query params:
        - page (int): Số trang, mặc định 1
        - per_page (int): Số item mỗi trang, mặc định 20
        - q (str): Từ khóa tìm kiếm (optional)

    Returns:
        HTTP 200: {'news': [...], 'page': 1, 'per_page': 20, 'total': ..., 'total_pages': ...}
    """
    page = request.args.get("page", 1, type=int)
    # Frontend có thể override per_page (VD: per_page=12)
    per_page = request.args.get("per_page", NEWS_PER_PAGE, type=int)
    query_str = request.args.get("q", "").strip()

    # Build query
    query = News.query
    if query_str:
        query = query.filter(News.title.ilike(f"%{query_str}%"))

    # Đếm tổng
    total = query.count()
    total_pages = max(1, (total + per_page - 1) // per_page)

    # Lấy dữ liệu theo thứ tự mới nhất
    news_items = (
        query.order_by(News.published_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return jsonify({
        "news": [item.to_dict() for item in news_items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    })


@news_bp.route("/fetch", methods=["POST"], strict_slashes=False)
def trigger_fetch():
    """
    Trigger fetch tin tức thủ công.

    What: Gọi fetch_and_save_news() ngay lập tức, không cần đợi scheduler
    Why: Dùng để seed data lần đầu hoặc debug
    How: Chỉ hoạt động khi DEBUG=True

    Returns:
        HTTP 200: {'message': '...', 'saved': count}
        HTTP 403: Nếu không phải môi trường development
    """
    if not current_app.config.get("DEBUG"):
        return jsonify({"error": "Chỉ hoạt động trong môi trường development"}), 403

    try:
        from app.services.crypto_news import fetch_and_save_news
        count = fetch_and_save_news()
        return jsonify({
            "message": f"Đã fetch và lưu {count} tin mới",
            "saved": count,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500