"""
Test News - Unit tests cho News Service & Routes.

Các test case trong Task 4.3:
1. Fetch lần 1 - lưu tin mới
2. Fetch lần 2 - không trùng lặp
3. GET danh sách - phân trang
4. GET tìm kiếm - lọc theo từ khóa
5. GET không có kết quả - trả 0
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from app.database import db
from app.models import News
from app.services.crypto_news import fetch_and_save_news, _parse_date


# =====================================================
# PARSE DATE TESTS
# =====================================================

class TestParseDate:
    """Test _parse_date function."""

    def test_parse_date_iso_format(self):
        """Test parse ISO format."""
        result = _parse_date("2024-01-01T12:00:00.000Z")
        assert result is not None
        assert result.year == 2024

    def test_parse_date_simple(self):
        """Test parse simple date."""
        result = _parse_date("2024-01-01")
        assert result is not None

    def test_parse_date_invalid(self):
        """Test parse invalid date."""
        result = _parse_date("invalid-date")
        assert result is None

    def test_parse_date_empty(self):
        """Test parse empty string."""
        result = _parse_date("")
        assert result is None


# =====================================================
# FETCH NEWS TESTS
# =====================================================

class TestFetchNews:
    """Test fetch_and_save_news function."""

    @patch("app.services.crypto_news.requests.get")
    def test_fetch_saves_new_articles(self, mock_get, app):
        """Test #1: Fetch lần 1 lưu tin mới."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "title": "Bitcoin hits $50k",
                "url": "https://example.com/1",
                "source": "CoinDesk",
                "description": "Bitcoin price",
                "image_url": "https://example.com/img.jpg",
                "published_at": "2024-01-01T12:00:00Z"
            },
            {
                "title": "Ethereum update",
                "url": "https://example.com/2",
                "source": "CoinTelegraph",
                "description": "Ethereum news",
                "published_at": "2024-01-02T12:00:00Z"
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with app.app_context():
            result = fetch_and_save_news()

        assert result == 2
        with app.app_context():
            count = News.query.count()
            assert count == 2

    @patch("app.services.crypto_news.requests.get")
    def test_fetch_no_duplicate(self, mock_get, app):
        """Test #2: Fetch lần 2 không trùng lặp."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "title": "Bitcoin hits $50k",
                "url": "https://example.com/1",
                "source": "CoinDesk",
                "published_at": "2024-01-01T12:00:00Z"
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with app.app_context():
            # Fetch lần 1
            result1 = fetch_and_save_news()
            # Fetch lần 2
            result2 = fetch_and_save_news()

        assert result1 == 1
        assert result2 == 0  # Không thêm vì đã tồn tại

    @patch("app.services.crypto_news.requests.get")
    def test_fetch_handles_dict_source(self, mock_get, app):
        """Test xử lý source là dict."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "title": "Test news",
                "url": "https://example.com/3",
                "source": {"name": "CoinDesk", "id": 1},
                "published_at": "2024-01-01T12:00:00Z"
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with app.app_context():
            fetch_and_save_news()
            news = News.query.first()

        assert news.source == "CoinDesk"


# =====================================================
# NEWS ROUTES TESTS
# =====================================================

class TestNewsRoutes:
    """Test news routes."""

    @pytest.fixture
    def sample_news(self, app):
        """Tạo news mẫu."""
        with app.app_context():
            news_items = [
                News(
                    title="Bitcoin news 1",
                    url="https://test.com/1",
                    source="Source1",
                    published_at=datetime(2024, 1, 1, tzinfo=timezone.utc)
                ),
                News(
                    title="Bitcoin news 2",
                    url="https://test.com/2",
                    source="Source2",
                    published_at=datetime(2024, 1, 2, tzinfo=timezone.utc)
                ),
                News(
                    title="Ethereum news",
                    url="https://test.com/3",
                    source="Source3",
                    published_at=datetime(2024, 1, 3, tzinfo=timezone.utc)
                ),
            ]
            db.session.add_all(news_items)
            db.session.commit()

    def test_get_news_list(self, client, sample_news):
        """Test #3: GET danh sách tin."""
        response = client.get("/api/news/")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "news" in data
        assert "page" in data
        assert "total" in data
        assert "total_pages" in data
        assert data["total"] == 3

    def test_search_news(self, client, sample_news):
        """Test #4: GET tìm kiếm theo từ khóa."""
        response = client.get("/api/news/?q=bitcoin")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "news" in data
        # Chỉ trả tin có "bitcoin"
        for item in data["news"]:
            assert "bitcoin" in item["title"].lower()

    def test_search_no_result(self, client, sample_news):
        """Test #5: GET không có kết quả."""
        response = client.get("/api/news/?q=xyznotexist")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["news"] == []
        assert data["total"] == 0
        assert data["total_pages"] == 0