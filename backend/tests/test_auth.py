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

Task 3.3 — Quản lý tài khoản (yêu cầu JWT):
Change Password:
1. Đổi mật khẩu thành công - trả 200
2. Mật khẩu hiện tại sai - trả 401
3. Mật khẩu mới quá ngắn - trả 400
4. Thiếu field - trả 400
5. Không có token - trả 401
6. Đăng nhập được bằng mật khẩu mới sau khi đổi

Change Username:
1. Đổi username thành công - trả 200, user mới
2. Mật khẩu xác nhận sai - trả 401
3. Username mới đã tồn tại - trả 409
4. Username quá ngắn - trả 400
5. Username trùng username hiện tại - trả 400
6. Không có token - trả 401

Delete Account:
1. Xóa tài khoản thành công - trả 200
2. Mật khẩu xác nhận sai - trả 401
3. Thiếu mật khẩu - trả 400
4. Không có token - trả 401
5. Sau khi xóa, login lại trả 401
6. Sau khi xóa, watchlist bị xóa cascade
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


# =====================================================
# CHANGE PASSWORD TESTS (Task 3.3)
# =====================================================

class TestChangePassword:
    """Test PATCH /api/auth/change-password."""

    # Dữ liệu user dùng xuyên suốt class này
    USERNAME = "pwuser"
    EMAIL = "pwuser@mail.com"
    PASSWORD = "oldpass123"

    @pytest.fixture(autouse=True)
    def setup_user_and_token(self, client):
        """Tạo user và lấy token trước mỗi test."""
        client.post("/api/auth/register", json={
            "username": self.USERNAME,
            "email": self.EMAIL,
            "password": self.PASSWORD
        })
        login = client.post("/api/auth/login", json={
            "username": self.USERNAME,
            "password": self.PASSWORD
        })
        self.token = login.get_json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_change_password_success(self, client):
        """Test #1: Đổi mật khẩu thành công - HTTP 200."""
        response = client.patch("/api/auth/change-password", json={
            "current_password": self.PASSWORD,
            "new_password": "newpass456"
        }, headers=self.headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data

    def test_change_password_wrong_current(self, client):
        """Test #2: Mật khẩu hiện tại sai - HTTP 401."""
        response = client.patch("/api/auth/change-password", json={
            "current_password": "wrongpass",
            "new_password": "newpass456"
        }, headers=self.headers)

        assert response.status_code == 401
        assert "error" in response.get_json()

    def test_change_password_new_too_short(self, client):
        """Test #3: Mật khẩu mới quá ngắn - HTTP 400."""
        response = client.patch("/api/auth/change-password", json={
            "current_password": self.PASSWORD,
            "new_password": "123"
        }, headers=self.headers)

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "6" in data["error"]

    def test_change_password_missing_field(self, client):
        """Test #4: Thiếu new_password - HTTP 400."""
        response = client.patch("/api/auth/change-password", json={
            "current_password": self.PASSWORD
        }, headers=self.headers)

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_change_password_no_token(self, client):
        """Test #5: Không có JWT token - HTTP 401."""
        response = client.patch("/api/auth/change-password", json={
            "current_password": self.PASSWORD,
            "new_password": "newpass456"
        })

        assert response.status_code == 401

    def test_can_login_with_new_password(self, client):
        """Test #6: Đăng nhập được bằng mật khẩu mới sau khi đổi."""
        new_password = "newpass456"
        client.patch("/api/auth/change-password", json={
            "current_password": self.PASSWORD,
            "new_password": new_password
        }, headers=self.headers)

        # Mật khẩu cũ không còn dùng được
        response_old = client.post("/api/auth/login", json={
            "username": self.USERNAME,
            "password": self.PASSWORD
        })
        assert response_old.status_code == 401

        # Mật khẩu mới đăng nhập được
        response_new = client.post("/api/auth/login", json={
            "username": self.USERNAME,
            "password": new_password
        })
        assert response_new.status_code == 200
        assert "access_token" in response_new.get_json()


# =====================================================
# CHANGE USERNAME TESTS (Task 3.3)
# =====================================================

class TestChangeUsername:
    """Test PATCH /api/auth/change-username."""

    USERNAME = "oldname"
    EMAIL = "nameuser@mail.com"
    PASSWORD = "pass123"

    @pytest.fixture(autouse=True)
    def setup_user_and_token(self, client):
        """Tạo user và lấy token trước mỗi test."""
        client.post("/api/auth/register", json={
            "username": self.USERNAME,
            "email": self.EMAIL,
            "password": self.PASSWORD
        })
        login = client.post("/api/auth/login", json={
            "username": self.USERNAME,
            "password": self.PASSWORD
        })
        self.token = login.get_json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_change_username_success(self, client):
        """Test #1: Đổi username thành công - HTTP 200 với user mới."""
        response = client.patch("/api/auth/change-username", json={
            "new_username": "newname",
            "current_password": self.PASSWORD
        }, headers=self.headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data
        assert "user" in data
        assert data["user"]["username"] == "newname"

    def test_change_username_wrong_password(self, client):
        """Test #2: Mật khẩu xác nhận sai - HTTP 401."""
        response = client.patch("/api/auth/change-username", json={
            "new_username": "newname",
            "current_password": "wrongpass"
        }, headers=self.headers)

        assert response.status_code == 401
        assert "error" in response.get_json()

    def test_change_username_already_taken(self, client):
        """Test #3: Username mới đã bị người khác dùng - HTTP 409."""
        # Tạo user thứ 2
        client.post("/api/auth/register", json={
            "username": "takenname",
            "email": "taken@mail.com",
            "password": "pass123"
        })

        response = client.patch("/api/auth/change-username", json={
            "new_username": "takenname",
            "current_password": self.PASSWORD
        }, headers=self.headers)

        assert response.status_code == 409
        assert "error" in response.get_json()

    def test_change_username_too_short(self, client):
        """Test #4: Username mới quá ngắn - HTTP 400."""
        response = client.patch("/api/auth/change-username", json={
            "new_username": "ab",
            "current_password": self.PASSWORD
        }, headers=self.headers)

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_change_username_same_as_current(self, client):
        """Test #5: Username mới trùng username hiện tại - HTTP 400."""
        response = client.patch("/api/auth/change-username", json={
            "new_username": self.USERNAME,
            "current_password": self.PASSWORD
        }, headers=self.headers)

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_change_username_no_token(self, client):
        """Test #6: Không có JWT token - HTTP 401."""
        response = client.patch("/api/auth/change-username", json={
            "new_username": "newname",
            "current_password": self.PASSWORD
        })

        assert response.status_code == 401


# =====================================================
# DELETE ACCOUNT TESTS (Task 3.3)
# =====================================================

class TestDeleteAccount:
    """Test DELETE /api/auth/delete-account."""

    USERNAME = "deleteuser"
    EMAIL = "deleteuser@mail.com"
    PASSWORD = "pass123"

    @pytest.fixture(autouse=True)
    def setup_user_and_token(self, client):
        """Tạo user và lấy token trước mỗi test."""
        client.post("/api/auth/register", json={
            "username": self.USERNAME,
            "email": self.EMAIL,
            "password": self.PASSWORD
        })
        login = client.post("/api/auth/login", json={
            "username": self.USERNAME,
            "password": self.PASSWORD
        })
        self.token = login.get_json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_delete_account_success(self, client):
        """Test #1: Xóa tài khoản thành công - HTTP 200."""
        response = client.delete("/api/auth/delete-account", json={
            "current_password": self.PASSWORD
        }, headers=self.headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data

    def test_delete_account_wrong_password(self, client):
        """Test #2: Mật khẩu xác nhận sai - HTTP 401."""
        response = client.delete("/api/auth/delete-account", json={
            "current_password": "wrongpass"
        }, headers=self.headers)

        assert response.status_code == 401
        assert "error" in response.get_json()

    def test_delete_account_missing_password(self, client):
        """Test #3: Thiếu trường current_password - HTTP 400."""
        response = client.delete("/api/auth/delete-account", json={},
                                 headers=self.headers)

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_delete_account_no_token(self, client):
        """Test #4: Không có JWT token - HTTP 401."""
        response = client.delete("/api/auth/delete-account", json={
            "current_password": self.PASSWORD
        })

        assert response.status_code == 401

    def test_cannot_login_after_delete(self, client):
        """Test #5: Sau khi xóa, login lại trả 401."""
        # Xóa tài khoản
        client.delete("/api/auth/delete-account", json={
            "current_password": self.PASSWORD
        }, headers=self.headers)

        # Thử login lại
        response = client.post("/api/auth/login", json={
            "username": self.USERNAME,
            "password": self.PASSWORD
        })

        assert response.status_code == 401

    def test_watchlist_cascade_deleted(self, client, app):
        """Test #6: Watchlist bị xóa cascade khi xóa tài khoản."""
        from app.models import Watchlist, db

        # Tạo watchlist item trực tiếp trong DB
        with app.app_context():
            from app.models import User, Coin
            user = User.query.filter_by(username=self.USERNAME).first()

            # Đảm bảo có coin để thêm watchlist
            coin = Coin.query.first()
            if coin is None:
                coin = Coin(id="bitcoin", symbol="btc", name="Bitcoin", image="")
                db.session.add(coin)
                db.session.commit()

            watchlist_item = Watchlist(user_id=user.id, coin_id=coin.id)
            db.session.add(watchlist_item)
            db.session.commit()
            user_id = user.id

        # Xóa tài khoản
        client.delete("/api/auth/delete-account", json={
            "current_password": self.PASSWORD
        }, headers=self.headers)

        # Kiểm tra watchlist đã bị xóa cascade
        with app.app_context():
            remaining = Watchlist.query.filter_by(user_id=user_id).count()
            assert remaining == 0