"""
Crypto News Service.

What: Fetch tin tức crypto từ RSS feeds của các nguồn uy tín
Why: cryptocurrency.cv/api/news đã chuyển sang paid (HTTP 402)
How: Parse RSS XML từ CoinDesk + CoinTelegraph bằng stdlib xml.etree

Nguồn:
- CoinDesk: https://feeds.feedburner.com/CoinDesk
- CoinTelegraph: https://cointelegraph.com/rss
"""

import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional
import xml.etree.ElementTree as ET

import requests

from app.models import db, News

logger = logging.getLogger(__name__)

# Cấu hình: các RSS feed nguồn tin tức crypto uy tín
RSS_FEEDS = [
    {
        "url": "https://feeds.feedburner.com/CoinDesk",
        "source": "CoinDesk",
    },
    {
        "url": "https://cointelegraph.com/rss",
        "source": "CoinTelegraph",
    },
]

TIMEOUT = 15  # giây


def _parse_rss_date(date_str: str) -> Optional[datetime]:
    """
    Parse chuỗi date theo chuẩn RFC 2822 (dùng trong RSS).

    Args:
        date_str: Ví dụ "Sat, 09 May 2026 17:28:08 +0000"

    Returns:
        datetime aware (UTC) hoặc None nếu parse fail
    """
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        logger.warning(f"Không parse được date RSS: {date_str!r}")
        return None


def _get_media_url(item: ET.Element, ns: dict) -> Optional[str]:
    """
    Lấy URL ảnh từ media:content element trong RSS item.

    Args:
        item: XML element <item>
        ns: namespace mapping

    Returns:
        URL ảnh hoặc None
    """
    # Thử media:content
    media = item.find("media:content", ns)
    if media is not None:
        return media.get("url")

    # Thử enclosure
    enclosure = item.find("enclosure")
    if enclosure is not None:
        enc_type = enclosure.get("type", "")
        if enc_type.startswith("image"):
            return enclosure.get("url")

    return None


def _fetch_rss_items(feed_url: str, source_name: str) -> list[dict]:
    """
    Fetch và parse một RSS feed.

    Args:
        feed_url: URL của RSS feed
        source_name: Tên nguồn (dùng làm field source trong DB)

    Returns:
        List các dict với các keys: title, url, description, image_url,
        published_at, source
    """
    try:
        response = requests.get(
            feed_url,
            timeout=TIMEOUT,
            headers={"User-Agent": "CryptoTracker/1.0 (+https://github.com)"},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Lỗi khi fetch RSS {source_name}: {e}")
        return []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        logger.error(f"Lỗi parse XML từ {source_name}: {e}")
        return []

    # Namespace mapping cho media:content
    ns = {
        "media": "http://search.yahoo.com/mrss/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "content": "http://purl.org/rss/1.0/modules/content/",
    }

    items = []

    # Tìm tất cả <item> trong RSS channel
    channel = root.find("channel")
    if channel is None:
        logger.warning(f"{source_name}: Không tìm thấy <channel> trong RSS")
        return []

    for item_el in channel.findall("item"):
        try:
            # Lấy các field từ XML element
            title_el = item_el.find("title")
            link_el = item_el.find("link")
            desc_el = item_el.find("description")
            pub_el = item_el.find("pubDate")

            title = title_el.text if title_el is not None else ""
            url = link_el.text if link_el is not None else ""
            description = desc_el.text if desc_el is not None else ""

            # Bỏ qua item không có URL
            if not url or not url.strip():
                continue

            url = url.strip()

            # Parse ngày đăng
            published_at = None
            if pub_el is not None and pub_el.text:
                published_at = _parse_rss_date(pub_el.text.strip())
            if published_at is None:
                published_at = datetime.now(timezone.utc)

            # Lấy ảnh thumbnail
            image_url = _get_media_url(item_el, ns)

            items.append({
                "title": title.strip() if title else "",
                "url": url,
                "description": description.strip() if description else None,
                "image_url": image_url,
                "published_at": published_at,
                "source": source_name,
            })

        except Exception as e:
            logger.error(f"Lỗi xử lý RSS item từ {source_name}: {e}")
            continue

    logger.info(f"Đã parse {len(items)} items từ {source_name}")
    return items


def fetch_and_save_news() -> int:
    """
    Fetch tin tức từ tất cả RSS feeds và lưu vào DB.

    Logic:
    - Fetch từ CoinDesk + CoinTelegraph
    - Bỏ qua URL đã tồn tại trong DB
    - Commit một lần sau toàn bộ vòng lặp

    Returns:
        Số tin mới được lưu vào DB
    """
    all_items: list[dict] = []

    # Fetch từ tất cả nguồn RSS
    for feed in RSS_FEEDS:
        items = _fetch_rss_items(feed["url"], feed["source"])
        all_items.extend(items)

    if not all_items:
        logger.warning("Không lấy được tin tức từ bất kỳ nguồn nào")
        return 0

    new_count = 0

    for item in all_items:
        try:
            url = item["url"]

            # Bỏ qua nếu URL đã có trong DB
            if News.query.filter_by(url=url).first():
                continue

            news = News(
                title=item["title"],
                url=url,
                source=item["source"],
                description=item.get("description"),
                image_url=item.get("image_url"),
                published_at=item["published_at"],
            )
            db.session.add(news)
            new_count += 1

        except Exception as e:
            logger.error(f"Lỗi khi xử lý tin: {e}")
            continue

    # Commit một lần sau vòng lặp (hiệu quả hơn commit từng record)
    if new_count > 0:
        try:
            db.session.commit()
            logger.info(f"Đã lưu {new_count} tin mới vào DB")
        except Exception as e:
            logger.error(f"Lỗi khi commit news: {e}")
            db.session.rollback()
            return 0

    return new_count