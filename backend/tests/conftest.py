"""
conftest.py — Shared pytest fixtures cho toàn bộ test suite.

What: Khai báo fixtures dùng chung giữa các test modules
Why: Tránh duplicate code và đảm bảo consistent setup/teardown
How: pytest tự động load conftest.py trong cùng thư mục trước khi chạy test
"""

import sys
from unittest.mock import MagicMock

import pytest



from app import create_app
from app.database import db


@pytest.fixture
def app():
    """
    Tạo Flask app với TestingConfig (SQLite in-memory) cho mỗi test.

    - Tự động create_all() trước khi test chạy
    - Tự động drop_all() sau khi test kết thúc (isolation tuyệt đối)
    """
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Tạo Flask test client từ app fixture."""
    return app.test_client()
