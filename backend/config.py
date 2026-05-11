"""
Module cấu hình cho Crypto Tracker Backend.

File này định nghĩa các class cấu hình cho các môi trường khác nhau:
- DevelopmentConfig: Cho phát triển local
- TestingConfig: Cho chạy test với SQLite in-memory
- ProductionConfig: Cho deploy production

Mỗi class kế thừa từ class Config base và đọc giá trị từ environment variables
với giá trị mặc định an toàn cho development.
"""

import os
from datetime import timedelta


def _fix_database_url(url: str | None) -> str | None:
    """
    Chuyển đổi URL từ postgres:// → postgresql://.

    Railway PostgreSQL cấp URL dạng postgres:// nhưng SQLAlchemy 2.x
    đã xoá hỗ trợ prefix này, chỉ chấp nhận postgresql://.
    """
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    """Class cấu hình base chứa các cài đặt chung."""

    # Cài đặt Flask
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=30)

    # Cài đặt SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Cài đặt CORS
    CORS_HEADERS: str = "Content-Type"

    # Cài đặt APScheduler
    SCHEDULER_API_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "UTC"

    # Cài đặt chung
    JSON_SORT_KEYS: bool = False
    JSONIFY_PRETTYPRINT_REGULAR: bool = False


class DevelopmentConfig(Config):
    """Cấu hình môi trường phát triển."""

    DEBUG: bool = True
    TESTING: bool = False

    # Database URL cho development (có convert postgres:// → postgresql://)
    SQLALCHEMY_DATABASE_URI: str = _fix_database_url(os.environ.get("DATABASE_URL"))

    # Cài đặt riêng cho development
    SQLALCHEMY_ECHO: bool = False  # Đặt thành True để xem SQL queries trong log


class TestingConfig(Config):
    """Cấu hình môi trường test với SQLite in-memory."""

    DEBUG: bool = False
    TESTING: bool = True

    # SQLite in-memory database cho test nhanh
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"

    # Tắt CSRF cho testing
    WTF_CSRF_ENABLED: bool = False

    # Tắt scheduler trong môi trường test
    SCHEDULER_API_ENABLED: bool = False

    # JWT_SECRET_KEY cho testing (test secret key)
    JWT_SECRET_KEY: str = "test-secret-key-for-testing-only"
    SECRET_KEY: str = "test-secret-key-for-testing-only"


class ProductionConfig(Config):
    """Cấu hình môi trường production."""

    DEBUG: bool = False
    TESTING: bool = False

    # Database URL cho production - PHẢI set qua environment variable
    # Railway cấp dạng postgres://, cần convert sang postgresql:// cho SQLAlchemy 2.x
    SQLALCHEMY_DATABASE_URI: str = _fix_database_url(os.environ.get("DATABASE_URL", ""))

    # Cài đặt riêng cho production
    SQLALCHEMY_ECHO: bool = False

    # Cài đặt cookie bảo mật
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"


# Mapping cấu hình cho các môi trường khác nhau
config_by_name: dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}