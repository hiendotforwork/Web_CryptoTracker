"""
Test Services - Unit tests cho CoinGecko Service.

Các test case trong Task 4.1:
1. Fetch top coins - kiểm tra cấu trúc trả về
2. Fetch coin detail - kiểm tra cấu trúc trả về
3. Fetch coin history - kiểm tra cấu trúc trả về
4. Retry khi 429 - mock trả 429, kiểm tra retry 3 lần
5. Timeout trả None - mock timeout, trả None không crash
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.coingecko import (
    fetch_top_coins,
    fetch_coin_detail,
    fetch_coin_history,
    _get_with_retry,
)


class TestFetchCoins:
    """
    Test fetch functions với CoinGecko API thật.
    Đánh dấu @pytest.mark.integration vì gọi network.
    Chạy riêng với: pytest -m integration
    """

    @pytest.mark.integration
    def test_fetch_top_coins_structure(self):
        """Test #1: Fetch top coins trả về list đúng cấu trúc (real API)."""
        result = fetch_top_coins(1, 25)

        assert result is not None, "CoinGecko API không phản hồi hoặc đang bị rate limit"
        assert isinstance(result, list)
        assert len(result) > 0, "API trả list rỗng"
        coin = result[0]
        assert "id" in coin
        assert "symbol" in coin
        assert "current_price" in coin
        assert "image" in coin

    @pytest.mark.integration
    def test_fetch_coin_detail_structure(self):
        """Test #2: Fetch coin detail trả về dict đúng cấu trúc (real API)."""
        result = fetch_coin_detail("bitcoin")

        assert result is not None, "CoinGecko API không phản hồi hoặc đang bị rate limit"
        assert isinstance(result, dict)
        assert "market_data" in result
        assert "current_price" in result["market_data"]
        assert "usd" in result["market_data"]["current_price"]
        assert result["market_data"]["current_price"]["usd"] > 0

    @pytest.mark.integration
    def test_fetch_coin_history_structure(self):
        """Test #3: Fetch coin history trả về dict đúng cấu trúc (real API)."""
        result = fetch_coin_history("bitcoin", 7)

        assert result is not None, "CoinGecko API không phản hồi hoặc đang bị rate limit"
        assert isinstance(result, dict)
        assert "prices" in result
        assert isinstance(result["prices"], list)
        assert len(result["prices"]) > 0, "API trả prices rỗng"
        # Format: [[timestamp_ms, price], ...]
        point = result["prices"][0]
        assert isinstance(point, list)
        assert len(point) == 2
        assert isinstance(point[0], (int, float))
        assert isinstance(point[1], (int, float))


class TestRetryLogic:
    """Test retry logic với mock."""

    @patch("app.services.coingecko.requests.get")
    def test_retry_on_429(self, mock_get):
        """Test #4: Retry 3 lần khi 429, trả None."""
        # Mock response trả 429 liên tục
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        result = _get_with_retry("http://test.com/api", max_retries=3)
        
        # Phải retry 3 lần
        assert mock_get.call_count == 3
        # Trả None vì hết retry
        assert result is None

    @patch("app.services.coingecko.requests.get")
    def test_timeout_returns_none(self, mock_get):
        """Test #5: Timeout trả None, không raise exception."""
        # Mock request raise Timeout
        import requests
        mock_get.side_effect = requests.Timeout("Timeout")
        
        result = _get_with_retry("http://test.com/api", max_retries=3)
        
        # Trả None, không crash
        assert result is None

    @patch("app.services.coingecko.requests.get")
    def test_5xx_retry(self, mock_get):
        """Test retry khi 5xx server error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = _get_with_retry("http://test.com/api", max_retries=3)
        
        # Phải retry 3 lần
        assert mock_get.call_count == 3
        assert result is None

    @patch("app.services.coingecko.requests.get")
    def test_success_no_retry(self, mock_get):
        """Test thành công không retry."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response
        
        result = _get_with_retry("http://test.com/api", max_retries=3)
        
        # Chỉ gọi 1 lần, không retry
        assert mock_get.call_count == 1
        assert result == {"data": "test"}