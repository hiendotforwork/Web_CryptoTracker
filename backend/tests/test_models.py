"""
Test Models - Unit tests cho SQLAlchemy models.

Các test case trong Task 2.1:
1. Hash password - user.password_hash khác plaintext
2. Verify đúng - check_password() trả True
3. Verify sai - check_password() trả False
4. to_dict() User - không có password_hash
5. Trùng watchlist - IntegrityError
6. Cascade delete - xóa user → xóa watchlist
"""

import pytest
from app import create_app
from app.database import db
from app.models import User, Coin, Watchlist


@pytest.fixture
def app():
    """Tạo app testing với SQLite in-memory."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def session(app):
    """Tạo database session cho test."""
    with app.app_context():
        yield db.session


class TestUserPassword:
    """Test password hashing và verification."""

    def test_user_password_hash(self, app):
        """Test #1: Hash password - password_hash khác plaintext."""
        with app.app_context():
            user = User(username="alice", email="alice@test.com")
            user.set_password("secret123")
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            
            # Password hash phải khác plaintext
            assert user.password_hash != "secret123"
            # Werkzeug 3.x dùng scrypt, các version cũ dùng pbkdf2:sha256
            assert user.password_hash.startswith(("pbkdf2:sha256:", "scrypt:"))

    def test_user_check_password_correct(self, app):
        """Test #2: Verify đúng - check_password() trả True."""
        with app.app_context():
            user = User(username="bob", email="bob@test.com")
            user.set_password("secret123")
            db.session.add(user)
            db.session.commit()
            
            assert user.check_password("secret123") is True

    def test_user_check_password_wrong(self, app):
        """Test #3: Verify sai - check_password() trả False."""
        with app.app_context():
            user = User(username="charlie", email="charlie@test.com")
            user.set_password("secret123")
            db.session.add(user)
            db.session.commit()
            
            assert user.check_password("wrongpass") is False

    def test_user_to_dict_no_password(self, app):
        """Test #4: to_dict() User - không có password_hash."""
        with app.app_context():
            user = User(username="dave", email="dave@test.com")
            user.set_password("secret123")
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            
            user_dict = user.to_dict()
            
            # Phải có các key
            assert "id" in user_dict
            assert "username" in user_dict
            assert "email" in user_dict
            assert "created_at" in user_dict
            
            # KHÔNG được có password_hash
            assert "password_hash" not in user_dict


class TestWatchlistConstraint:
    """Test watchlist unique constraint."""

    def test_watchlist_unique_constraint(self, app):
        """Test #5: Trùng watchlist - IntegrityError."""
        with app.app_context():
            # Tạo user
            user = User(username="eve", email="eve@test.com")
            user.set_password("pass123")
            db.session.add(user)
            
            # Tạo coin
            coin = Coin(
                id="bitcoin",
                name="Bitcoin",
                symbol="btc"
            )
            db.session.add(coin)
            db.session.commit()
            
            # Thêm watchlist lần 1
            watchlist1 = Watchlist(user_id=user.id, coin_id="bitcoin")
            db.session.add(watchlist1)
            db.session.commit()
            
            # Thêm watchlist lần 2 (phải lỗi)
            watchlist2 = Watchlist(user_id=user.id, coin_id="bitcoin")
            db.session.add(watchlist2)
            
            with pytest.raises(Exception):  # IntegrityError trong SQLAlchemy
                db.session.commit()


class TestCascadeDelete:
    """Test cascade delete."""

    def test_cascade_delete(self, app):
        """Test #6: Xóa user → xóa watchlist."""
        with app.app_context():
            # Tạo user
            user = User(username="frank", email="frank@test.com")
            user.set_password("pass123")
            db.session.add(user)
            
            # Tạo coin
            coin = Coin(
                id="ethereum",
                name="Ethereum",
                symbol="eth"
            )
            db.session.add(coin)
            db.session.commit()
            
            # Thêm watchlist
            watchlist = Watchlist(user_id=user.id, coin_id="ethereum")
            db.session.add(watchlist)
            db.session.commit()
            
            # Lưu ID để kiểm tra
            watchlist_id = watchlist.id
            
            # Xóa user
            db.session.delete(user)
            db.session.commit()
            
            # Kiểm tra watchlist đã bị xóa theo
            deleted_watchlist = db.session.get(Watchlist, watchlist_id)
            assert deleted_watchlist is None