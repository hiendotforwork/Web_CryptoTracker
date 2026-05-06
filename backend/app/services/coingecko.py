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
from typing import Optional

import requests

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