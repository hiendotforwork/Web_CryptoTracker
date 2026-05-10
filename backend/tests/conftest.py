"""
conftest.py — Shared pytest fixtures cho toàn bộ test suite.

What: Khai báo fixtures dùng chung giữa các test modules
Why: Tránh duplicate code và đảm bảo consistent setup/teardown
How: pytest tự động load conftest.py trong cùng thư mục trước khi chạy test
"""

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


@pytest.fixture
def auth_headers(client):
    """
    Tạo user, đăng nhập và trả về Authorization headers sẵn dùng.

    What: Fixture tổng hợp register + login → trả dict headers
    Why: Nhiều test endpoint cần token → tránh lặp code setup
    How: Gọi /api/auth/register rồi /api/auth/login, lấy access_token

    Returns:
        dict: {'Authorization': 'Bearer <token>'}
    """
    # Đăng ký user test
    client.post("/api/auth/register", json={
        "username": "fixture_user",
        "email": "fixture@mail.com",
        "password": "pass123"
    })

    # Đăng nhập lấy token
    response = client.post("/api/auth/login", json={
        "username": "fixture_user",
        "password": "pass123"
    })
    token = response.get_json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
