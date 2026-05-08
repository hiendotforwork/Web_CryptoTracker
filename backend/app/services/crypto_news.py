"""
Crypto News Service.

Module này cung cấp hàm để fetch tin tức crypto từ API:
- fetch_and_save_news(): Fetch và lưu tin tức vào DB

Lưu ý:
- Commit một lần sau vòng lặp, không commit từng item
- Bỏ qua URL đã có trong DB
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import requests

from app.models import db, News

# Cấu hình
NEWS_API_URL = "https://cryptocurrency.cv/api/news"
TIMEOUT = 10  # giây

logger = logging.getLogger(__name__)


def _parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string thành datetime.

    Hỗ trợ nhiều format date, có fallback về datetime.now().

    Args:
        date_str: Chuỗi date cần parse

    Returns:
        datetime object hoặc None nếu parse fail
    """
    if not date_str:
        return None

    # Các format date thử theo thứ tự
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # 2024-01-01T12:00:00.000Z
        "%Y-%m-%dT%H:%M:%SZ",     # 2024-01-01T12:00:00Z
        "%Y-%m-%d %H:%M:%S",       # 2024-01-01 12:00:00
        "%Y-%m-%d",                # 2024-01-01
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    # Fallback: trả None để dùng datetime.now() ở caller
    logger.warning(f"Không parse được date: {date_str}")
    return None


def fetch_and_save_news() -> int:
    """
    Fetch tin tức crypto và lưu vào DB.

    Gọi API, parse response, bỏ qua URL đã có.
    Commit một lần sau vòng lặp.

    Returns:
        Số tin mới được lưu
    """
    try:
        response = requests.get(NEWS_API_URL, timeout=TIMEOUT)
        response.raise_for_status()
        news_data = response.json()
    except requests.RequestException as e:
        logger.error(f"Lỗi khi gọi News API: {e}")
        return 0

    if not isinstance(news_data, list):
        logger.warning("Response không phải list")
        return 0

    new_count = 0

    for item in news_data:
        try:
            # Lấy URL để kiểm tra trùng
            url = item.get("url")
            if not url:
                continue

            # Kiểm tra đã tồn tại chưa
            existing = News.query.filter_by(url=url).first()
            if existing:
                continue

            # Parse date
            published_at = _parse_date(item.get("published_at"))
            if published_at is None:
                published_at = datetime.now(timezone.utc)

            # Xử lý source (có thể là string hoặc dict)
            source = item.get("source")
            if isinstance(source, dict):
                source = source.get("name", "")

            # Tạo news mới
            news = News(
                title=item.get("title", ""),
                url=url,
                source=source,
                description=item.get("description"),
                image_url=item.get("image_url"),
                published_at=published_at,
            )
            db.session.add(news)
            new_count += 1

        except Exception as e:
            logger.error(f"Lỗi khi xử lý tin: {e}")
            continue

    # Commit một lần sau vòng lặp
    if new_count > 0:
        try:
            db.session.commit()
            logger.info(f"Đã lưu {new_count} tin mới")
        except Exception as e:
            logger.error(f"Lỗi khi commit: {e}")
            db.session.rollback()
            return 0

    return new_count