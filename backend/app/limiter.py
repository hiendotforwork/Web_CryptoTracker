"""
Limiter module.

What: Khởi tạo Flask-Limiter instance để dùng chung.
Why: Tách riêng để tránh circular import giữa __init__.py và các routes.
How: Import limiter này vào các route cần sử dụng (ví dụ auth.py).
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Khởi tạo instance duy nhất của Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
