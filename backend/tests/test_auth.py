"""
Test Auth - Unit tests cho Authentication API.

Các test case trong Task 3.1 (Register) và Task 3.2 (Login):
1. Register hợp lệ - trả 201, user object
2. Register trùng username - trả 409
3. Register trùng email - trả 409
4. Register password ngắn - trả 400
5. Register thiếu field - trả 400
6. Register body không JSON - trả 400
7. Register response không có password_hash

1. Login đúng - trả 200, access_token
2. Login sai username - trả 401
3. Login sai password - trả 401 (cùng message với sai username)
4. Login thiếu field - trả 400
5. Protected route với valid token - trả 200
6. Protected route với invalid token - trả 401
"""

import pytest
from app.models import User


# =====================================================
# REGISTER TESTS (Task 3.1)
# =====================================================

class TestRegister:
    """Test POST /api/auth/register."""

    def test_register_success(self, client):
        """Test #1: Register hợp lệ - HTTP 201."""
        response = client.post("/api/auth/register", json={
            "username": "alice",
            "email": "alice@mail.com",
            "password": "pass123"
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert "message" in data
        assert "user" in data
        assert data["user"]["username"] == "alice"
        assert data["user"]["email"] == "alice@mail.com"

    def test_register_duplicate_username(self, client):
        """Test #2: Trùng username - HTTP 409."""
        # Tạo user trước
        client.post("/api/auth/register", json={
            "username": "alice",
            "email": "alice1@mail.com",
            "password": "pass123"
        })
        
        # Register lần 2 với cùng username
        response = client.post("/api/auth/register", json={
            "username": "alice",
            "email": "alice2@mail.com",
            "password": "pass123"
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert "error" in data
        assert "Username đã tồn tại" in data["error"]

    def test_register_duplicate_email(self, client):
        """Test #3: Trùng email - HTTP 409."""
        # Tạo user trước
        client.post("/api/auth/register", json={
            "username": "alice1",
            "email": "alice@mail.com",
            "password": "pass123"
        })
        
        # Register lần 2 với cùng email
        response = client.post("/api/auth/register", json={
            "username": "alice2",
            "email": "alice@mail.com",
            "password": "pass123"
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert "error" in data
        assert "Email đã tồn tại" in data["error"]

    def test_register_short_password(self, client):
        """Test #4: Password ngắn - HTTP 400."""
        response = client.post("/api/auth/register", json={
            "username": "bob",
            "email": "bob@mail.com",
            "password": "123"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Mật khẩu phải ít nhất 6 ký tự" in data["error"]

    def test_register_missing_fields(self, client):
        """Test #5: Thiếu field - HTTP 400."""
        response = client.post("/api/auth/register", json={
            "username": "bob"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "điền đầy đủ" in data["error"].lower()

    def test_register_no_json(self, client):
        """Test #6: Body không JSON - HTTP 400."""
        response = client.post(
            "/api/auth/register",
            data="not json",
            content_type="text/plain"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "JSON" in data["error"]

    def test_register_no_password_hash_in_response(self, client):
        """Test #7: Response không có password_hash."""
        response = client.post("/api/auth/register", json={
            "username": "dave",
            "email": "dave@mail.com",
            "password": "pass123"
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        # key password_hash không được có trong response
        assert "password_hash" not in data["user"]


# =====================================================
# LOGIN TESTS (Task 3.2)
# =====================================================

class TestLogin:
    """Test POST /api/auth/login."""

    @pytest.fixture(autouse=True)
    def setup_user(self, client):
        """Tạo user để test login."""
        client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@mail.com",
            "password": "pass123"
        })

    def test_login_success(self, client):
        """Test #1: Login đúng - HTTP 200."""
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "pass123"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["username"] == "testuser"

    def test_login_wrong_username(self, client):
        """Test #2: Sai username - HTTP 401."""
        response = client.post("/api/auth/login", json={
            "username": "nobody",
            "password": "pass123"
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data

    def test_login_wrong_password(self, client):
        """Test #3: Sai password - HTTP 401 (cùng message)."""
        response_wrong_user = client.post("/api/auth/login", json={
            "username": "nobody",
            "password": "pass123"
        })
        
        response_wrong_pass = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrongpass"
        })
        
        # Cùng message lỗi
        assert response_wrong_user.status_code == 401
        assert response_wrong_pass.status_code == 401
        assert response_wrong_user.get_json()["error"] == response_wrong_pass.get_json()["error"]

    def test_login_missing_fields(self, client):
        """Test #4: Thiếu field - HTTP 400."""
        response = client.post("/api/auth/login", json={
            "username": "testuser"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "username" in data["error"].lower() or "password" in data["error"].lower()

    def test_login_no_json(self, client):
        """Test #5: Body không JSON - HTTP 400."""
        response = client.post(
            "/api/auth/login",
            data="not json",
            content_type="text/plain"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data


# =====================================================
# JWT TOKEN TESTS
# =====================================================

class TestJWTToken:
    """Test JWT token authentication."""

    @pytest.fixture(autouse=True)
    def setup_user(self, client):
        """Tạo user để test token."""
        client.post("/api/auth/register", json={
            "username": "tokenuser",
            "email": "token@mail.com",
            "password": "pass123"
        })

    def test_protected_with_valid_token(self, client):
        """Test #5: Valid token - HTTP 200 (trả về watchlist rỗng của user)."""
        login_response = client.post("/api/auth/login", json={
            "username": "tokenuser",
            "password": "pass123"
        })
        token = login_response.get_json()["access_token"]
        
        # Dùng trailing slash để tránh 308 redirect
        response = client.get(
            "/api/watchlist/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200

    def test_protected_with_invalid_token(self, client):
        """Test #6: Invalid token - HTTP 401."""
        # Dùng trailing slash để tránh Flask redirect 308 trước khi kiểm tra JWT
        response = client.get(
            "/api/watchlist/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401