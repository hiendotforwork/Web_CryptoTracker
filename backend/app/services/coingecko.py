"""
CoinGecko API Service.

Module này cung cấp các hàm để gọi CoinGecko API:
- fetch_top_coins(): Lấy danh sách top coins
- fetch_coin_detail(): Lấy chi tiết một coin
- fetch_coin_history(): Lấy lịch sử giá coin

Lưu ý:
- Giới hạn 15 calls/phút theo CoinGecko free plan
- Dùng exponential backoff khi bị rate limit
"""

import logging
import time
from datetime import datetime, timezone
from typing import Optional

import requests

from app.models import db, Coin, PriceHistory

# Cấu hình
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
MAX_RETRIES = 3
TIMEOUT = 10  # giây

logger = logging.getLogger(__name__)


def _get_with_retry(url: str, params: Optional[dict] = None, max_retries: int = MAX_RETRIES) -> Optional[dict]:
    """
    Gọi API với retry exponential backoff.

    Args:
        url: URL cần gọi
        params: Query parameters
        max_retries: Số lần retry tối đa

    Returns:
        Response JSON hoặc None nếu thất bại
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT)
            
            # Xử lý các status codes
            if response.status_code == 200:
                return response.json()
            
            # 429: Rate limit - chờ và retry
            if response.status_code == 429:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(f"Rate limit. Retry sau {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            # 5xx: Server error - retry
            if response.status_code >= 500:
                wait_time = 2 ** attempt
                logger.warning(f"Server error {response.status_code}. Retry sau {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            # Các lỗi khác
            logger.error(f"API error: {response.status_code}")
            return None
            
        except requests.Timeout:
            logger.error(f"Timeout khi gọi {url}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 ** attempt)
            
        except Exception as e:
            logger.error(f"Lỗi khi gọi API: {e}")
            return None
    
    logger.error(f"Hết số lần retry sau {max_retries} lần thử")
    return None


def fetch_top_coins(page: int = 1, per_page: int = 25) -> Optional[list]:
    """
    Lấy danh sách top coins theo vốn hóa.

    Args:
        page: Số trang
        per_page: Số coins/trang (tối đa 250)

    Returns:
        List coins hoặc None nếu thất bại
    """
    url = f"{COINGECKO_API_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": False,
    }
    
    data = _get_with_retry(url, params)
    return data if isinstance(data, list) else None


def fetch_coin_detail(coin_id: str) -> Optional[dict]:
    """
    Lấy chi tiết một coin.

    Args:
        coin_id: ID của coin (vd: bitcoin, ethereum)

    Returns:
        Dict chứa thông tin coin hoặc None
    """
    url = f"{COINGECKO_API_URL}/coins/{coin_id}"
    params = {
        "localization": False,
        "tickers": False,
        "market_data": True,
        "community_data": False,
        "developer_data": False,
        "sparkline": False,
    }
    
    return _get_with_retry(url, params)


def fetch_coin_history(coin_id: str, days: int = 7) -> Optional[dict]:
    """
    Lấy lịch sử giá của một coin.

    Args:
        coin_id: ID của coin
        days: Số ngày lịch sử

    Returns:
        Dict chứa prices hoặc None
    """
    url = f"{COINGECKO_API_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
    }
    
    return _get_with_retry(url, params)


def _parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string thành datetime.
    Hỗ trợ nhiều format date, có fallback về None.
    """
    if not date_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def fetch_and_save_coins() -> int:
    """
    Fetch top coins và lưu vào DB.
    
    Gọi API fetch_top_coins từ service coingecko.
    Lưu/cập nhật thông tin từng coin vào bảng coins.
    Lưu giá hiện tại vào bảng price_history.
    Commit một lần sau vòng lặp.
    
    Returns:
        Số coin được cập nhật thành công
    """
    try:
        coins_data = fetch_top_coins(per_page=100)
    except Exception as e:
        logger.error(f"Lỗi khi gọi fetch_top_coins: {e}")
        return 0

    if not coins_data:
        logger.warning("Không lấy được dữ liệu coins")
        return 0

    new_count = 0

    for item in coins_data:
        try:
            coin_id = item.get("id")
            if not coin_id:
                continue

            # Kiểm tra coin đã tồn tại chưa
            coin = Coin.query.get(coin_id)
            if not coin:
                coin = Coin(id=coin_id)
                db.session.add(coin)
            
            # Cập nhật thông tin coin
            coin.name = item.get("name", "")
            coin.symbol = item.get("symbol", "")
            coin.image = item.get("image", "")
            coin.current_price = item.get("current_price", 0)
            coin.market_cap = item.get("market_cap", 0)
            coin.market_cap_rank = item.get("market_cap_rank")
            coin.volume = item.get("total_volume", 0)
            coin.price_change_24h = item.get("price_change_24h", 0)
            coin.price_change_percentage_24h = item.get("price_change_percentage_24h", 0)
            coin.circulating_supply = item.get("circulating_supply", 0)
            coin.total_supply = item.get("total_supply", 0)
            coin.ath = item.get("ath", 0)
            coin.ath_change_percentage = item.get("ath_change_percentage", 0)
            
            coin.ath_date = _parse_date(item.get("ath_date"))
            
            coin.atl = item.get("atl", 0)
            coin.atl_change_percentage = item.get("atl_change_percentage", 0)
            coin.atl_date = _parse_date(item.get("atl_date"))
            
            coin.last_updated = datetime.now(timezone.utc)

            # Tạo record PriceHistory nếu có current_price
            if coin.current_price is not None:
                history = PriceHistory(
                    coin_id=coin.id,
                    price=coin.current_price,
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(history)

            new_count += 1

        except Exception as e:
            logger.error(f"Lỗi khi xử lý coin {item.get('id')}: {e}")
            continue

    # Commit một lần sau vòng lặp
    if new_count > 0:
        try:
            db.session.commit()
            logger.info(f"Đã cập nhật {new_count} coins")
        except Exception as e:
            logger.error(f"Lỗi khi commit: {e}")
            db.session.rollback()
            return 0

    return new_count