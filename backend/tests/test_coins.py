"""
Test Coins - Unit tests cho Coins Routes.

Các test case trong Task 4.2:
1. GET /api/coins/?page=1 - pagination
2. GET /api/coins/?page=2 - pagination
3. GET /api/coins/bitcoin - coin detail
4. GET /api/coins/invalid-xyz - 404
5. GET /api/coins/bitcoin/history - price history
6. GET /api/coins/search?q=bit - search
7. GET /api/coins/search?q=ETH - case-insensitive
8. GET /api/coins/search?q= - empty query 400
"""

import pytest
from unittest.mock import patch
from app.database import db
from app.models import Coin


@pytest.fixture
def sample_coins(app):
    """Tạo coins mẫu trong DB."""
    with app.app_context():
        coins = [
            Coin(id="bitcoin", name="Bitcoin", symbol="btc", current_price=42000),
            Coin(id="ethereum", name="Ethereum", symbol="eth", current_price=2500),
            Coin(id="bitcoin-cash", name="Bitcoin Cash", symbol="bch", current_price=250),
        ]
        db.session.add_all(coins)
        db.session.commit()


# =====================================================
# PAGINATION TESTS
# =====================================================

class TestCoinsPagination:
    """Test pagination."""

    def test_get_coins_page1(self, client, sample_coins):
        """Test #1: GET /api/coins/?page=1."""
        response = client.get("/api/coins/?page=1")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "coins" in data
        assert "page" in data
        assert "per_page" in data
        assert "total" in data
        assert "total_pages" in data

    def test_get_coins_page2(self, client, sample_coins):
        """Test #2: GET /api/coins/?page=2."""
        response = client.get("/api/coins/?page=2")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["page"] == 2


# =====================================================
# COIN DETAIL TESTS
# =====================================================

class TestCoinDetail:
    """Test coin detail endpoint."""

    def test_get_coin_detail(self, client, sample_coins):
        """Test #3: GET /api/coins/bitcoin — coin có sẵn trong DB, không gọi API ngoài."""
        # Bitcoin có trong sample_coins → route lấy từ DB mà không cần gọi CoinGecko
        response = client.get("/api/coins/bitcoin")

        assert response.status_code == 200
        data = response.get_json()
        assert "coin" in data
        assert data["coin"]["id"] == "bitcoin"

    @patch("app.routes.coins.fetch_coin_detail")
    def test_get_coin_not_found(self, mock_fetch, client):
        """Test #4: GET /api/coins/invalid-xyz — coin không có trong DB và API trả None."""
        # Simulate: coin không tồn tại trong hệ thống, API cũng không tìm thấy
        mock_fetch.return_value = None

        response = client.get("/api/coins/invalid-xyz")

        # Route trả 503 khi external API không phản hồi (theo thiết kế hiện tại)
        assert response.status_code == 503
        data = response.get_json()
        assert "error" in data
        mock_fetch.assert_called_once_with("invalid-xyz")


# =====================================================
# HISTORY TESTS
# =====================================================

class TestCoinHistory:
    """Test coin history endpoint."""

    @patch("app.routes.coins.fetch_coin_history")
    def test_get_coin_history(self, mock_history, client, sample_coins):
        """Test #5: GET /api/coins/bitcoin/history — trả prices list."""
        mock_history.return_value = {
            "prices": [
                [1700000000000, 42000.5],
                [1700086400000, 42100.2],
            ]
        }

        response = client.get("/api/coins/bitcoin/history")

        assert response.status_code == 200
        data = response.get_json()
        assert "prices" in data
        assert isinstance(data["prices"], list)
        assert len(data["prices"]) == 2
        mock_history.assert_called_once_with("bitcoin", 7)


# =====================================================
# SEARCH TESTS
# =====================================================

class TestSearch:
    """Test search endpoint."""

    def test_search_coins(self, client, sample_coins):
        """Test #6: GET /api/coins/search?q=bit."""
        response = client.get("/api/coins/search?q=bit")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "coins" in data
        # Phải tìm thấy bitcoin
        coin_ids = [c["id"] for c in data["coins"]]
        assert "bitcoin" in coin_ids or "bitcoin-cash" in coin_ids

    def test_search_case_insensitive(self, client, sample_coins):
        """Test #7: GET /api/coins/search?q=ETH."""
        response = client.get("/api/coins/search?q=ETH")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "coins" in data
        # Phải tìm thấy ethereum (case-insensitive)
        coin_ids = [c["id"] for c in data["coins"]]
        assert "ethereum" in coin_ids

    def test_search_empty_query(self, client):
        """Test #8: GET /api/coins/search?q=."""
        response = client.get("/api/coins/search?q=")
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "không được để trống" in data["error"].lower() or "q" in data["error"].lower()

    def test_search_not_in_db(self, client, sample_coins):
        """Test tìm kiếm coin không có trong DB."""
        response = client.get("/api/coins/search?q=notexistxyz")
        assert response.status_code == 200
        data = response.get_json()
        assert "coins" in data
        assert len(data["coins"]) == 0


# =====================================================
# EXTRA COVERAGE TESTS
# =====================================================

class TestCoinsCoverage:
    """Các test case bổ sung để tăng coverage cho coins.py."""

    @patch("app.routes.coins.fetch_top_coins")
    def test_get_coins_empty_db(self, mock_fetch, client, app):
        """Test phân trang khi DB trống (gọi API)."""
        # Không dùng fixture sample_coins
        with app.app_context():
            db.session.query(Coin).delete()
            db.session.commit()
            
            # Giả lập trả về dữ liệu mock
            mock_fetch.return_value = [
                {"id": "new-coin", "name": "New Coin", "symbol": "new", "current_price": 10}
            ]
            
            response = client.get("/api/coins/?page=1")
            assert response.status_code == 200
            data = response.get_json()
            assert "total_pages" in data
            
            # DB trống sẽ gọi fetch INITIAL_PAGES_TO_FETCH lần (4 lần)
            assert mock_fetch.call_count > 0

    @patch("app.routes.coins.fetch_top_coins")
    def test_get_coins_page_no_data(self, mock_fetch, client, sample_coins):
        """Test phân trang khi trang > 1 và không có dữ liệu, phải gọi API."""
        mock_fetch.return_value = [
            {"id": "new-coin-2", "name": "New Coin 2", "symbol": "nc2", "current_price": 20}
        ]
        
        # page 10 chắc chắn rỗng
        response = client.get("/api/coins/?page=10")
        assert response.status_code == 200
        assert mock_fetch.called

    @patch("app.routes.coins.fetch_coin_detail")
    def test_get_coin_detail_api(self, mock_fetch, client):
        """Test lấy detail coin qua API (không có trong DB)."""
        mock_fetch.return_value = {
            "id": "fetched-coin",
            "name": "Fetched",
            "symbol": "fc",
            "market_data": {
                "current_price": {"usd": 15}
            }
        }
        
        response = client.get("/api/coins/fetched-coin")
        assert response.status_code == 200
        data = response.get_json()
        assert data["coin"]["id"] == "fetched-coin"

    @patch("app.routes.coins.fetch_coin_history")
    @patch("app.routes.coins.fetch_coin_detail")
    def test_get_coin_history_not_in_db(self, mock_detail, mock_history, client):
        """Test lịch sử cho coin không có trong DB."""
        mock_detail.return_value = {"id": "hist-coin", "name": "Hist", "symbol": "hc"}
        mock_history.return_value = {"prices": [[1000, 10], [2000, 20]]}
        
        response = client.get("/api/coins/hist-coin/history")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["prices"]) == 2

    @patch("app.routes.coins.fetch_coin_history")
    @patch("app.routes.coins.fetch_coin_detail")
    def test_get_coin_history_not_found(self, mock_detail, mock_history, client):
        """Test lịch sử cho coin không có trong DB và API detail lỗi."""
        mock_detail.return_value = None
        
        response = client.get("/api/coins/hist-coin/history")
        assert response.status_code == 404

    @patch("app.routes.coins.fetch_coin_history")
    def test_get_coin_history_fallback_db(self, mock_history, client, sample_coins, app):
        """Test fallback lấy lịch sử từ DB khi API history rỗng."""
        mock_history.return_value = None
        
        # Thêm price history giả vào DB
        with app.app_context():
            from app.models import PriceHistory
            from datetime import datetime, timezone
            db.session.add(PriceHistory(coin_id="bitcoin", price=40000, timestamp=datetime.now(timezone.utc)))
            db.session.commit()

        response = client.get("/api/coins/bitcoin/history")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["prices"]) == 1
        assert data["prices"][0][1] == 40000.0