"""
Test Watchlist - Unit tests cho Watchlist Routes.

Các test case trong Task 4.4:
1. GET không token - 401
2. POST thêm coin - 201
3. POST trùng coin - 409
4. POST coin không tồn tại - 404
5. GET có token - 200
6. DELETE coin - 200
7. DELETE lần 2 - 404
"""

import pytest
from app.database import db
from app.models import User, Coin, Watchlist


@pytest.fixture
def auth_token(client):
    """Tạo user và lấy token."""
    # Register user
    client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@mail.com",
        "password": "pass123"
    })
    
    # Login để lấy token
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "pass123"
    })
    return response.get_json()["access_token"]


@pytest.fixture
def sample_coins(app):
    """Tạo coins mẫu."""
    with app.app_context():
        coins = [
            Coin(id="bitcoin", name="Bitcoin", symbol="btc", current_price=42000),
            Coin(id="ethereum", name="Ethereum", symbol="eth", current_price=2500),
        ]
        db.session.add_all(coins)
        db.session.commit()


# =====================================================
# AUTH TESTS
# =====================================================

class TestWatchlistAuth:
    """Test authentication."""

    def test_get_watchlist_no_auth(self, client):
        """Test #1: GET không có token - 401."""
        response = client.get("/api/watchlist/")
        
        assert response.status_code == 401


# =====================================================
# CRUD TESTS
# =====================================================

class TestWatchlistCrud:
    """Test watchlist CRUD."""

    def test_add_coin(self, client, auth_token, sample_coins):
        """Test #2: POST thêm coin - 201."""
        response = client.post(
            "/api/watchlist/",
            json={"coin_id": "bitcoin"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert "message" in data
        assert "item" in data

    def test_add_duplicate_coin(self, client, auth_token, sample_coins):
        """Test #3: POST trùng coin - 409."""
        # Thêm lần 1
        client.post(
            "/api/watchlist/",
            json={"coin_id": "bitcoin"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Thêm lần 2
        response = client.post(
            "/api/watchlist/",
            json={"coin_id": "bitcoin"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 409
        data = response.get_json()
        assert "error" in data
        assert "đã có" in data["error"].lower()

    def test_add_nonexistent_coin(self, client, auth_token):
        """Test #4: POST coin không tồn tại - 404."""
        response = client.post(
            "/api/watchlist/",
            json={"coin_id": "not-exist"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert "không tồn tại" in data["error"].lower()

    def test_get_watchlist(self, client, auth_token, sample_coins):
        """Test #5: GET có token - 200."""
        # Thêm coin trước
        client.post(
            "/api/watchlist/",
            json={"coin_id": "bitcoin"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # GET watchlist
        response = client.get(
            "/api/watchlist/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "watchlist" in data

    def test_delete_coin(self, client, auth_token, sample_coins):
        """Test #6: DELETE coin - 200."""
        # Thêm coin trước
        client.post(
            "/api/watchlist/",
            json={"coin_id": "bitcoin"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # DELETE
        response = client.delete(
            "/api/watchlist/bitcoin",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data

    def test_delete_nonexistent(self, client, auth_token):
        """Test #7: DELETE lần 2 - 404."""
        # DELETE (không có trong watchlist)
        response = client.delete(
            "/api/watchlist/bitcoin",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data