"""
Database module - SQLAlchemy instance.

Module này khởi tạo một SQLAlchemy instance duy nhất
để dùng chung cho tất cả models.

Tại sao tách ra file riêng:
- Tránh tạo nhiều SQLAlchemy instances
- Đảm bảo tất cả models dùng cùng một db instance
- Import trong models: from app.database import db
"""

from flask_sqlalchemy import SQLAlchemy

# Khởi tạo SQLAlchemy instance DUY NHẤT
# Đây là instance duy nhất được dùng cho tất cả models
db = SQLAlchemy()