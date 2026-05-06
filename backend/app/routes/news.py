"""
News routes module.

Định nghĩa các routes cho news:
- GET /api/news/: Danh sách tin tức có phân trang
- GET /api/news/search: Tìm kiếm tin tức
"""

from flask import Blueprint, request, jsonify
from app.models import db, News

# Khởi tạo Blueprint
news_bp = Blueprint("news", __name__)

# Cấu hình phân trang
NEWS_PER_PAGE = 20


@news_bp.route("/", methods=["GET"])
def get_news():
    """
    Lấy danh sách tin tức có phân trang.

    Query params:
        - page (int): Số trang, mặc định 1
        - q (str): Từ khóa tìm kiếm (optional)

    Returns:
        HTTP 200: {'news': [...], 'page': 1, 'per_page': 20, 'total': ..., 'total_pages': ...}
    """
    page = request.args.get("page", 1, type=int)
    per_page = NEWS_PER_PAGE
    query_str = request.args.get("q", "").strip()

    # Build query
    query = News.query
    if query_str:
        query = query.filter(News.title.ilike(f"%{query_str}%"))

    # Đếm tổng
    total = query.count()
    total_pages = (total + per_page - 1) // per_page

    # Lấy dữ liệu
    news_items = query.order_by(News.published_at.desc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    return jsonify({
        "news": [item.to_dict() for item in news_items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages
    })