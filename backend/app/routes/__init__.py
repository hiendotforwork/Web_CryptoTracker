"""
Routes package - Export all blueprints.

Module này export tất cả blueprints để đăng ký trong app.

Ví dụ sử dụng:
    from app.routes import auth_bp, coins_bp, news_bp, watchlist_bp
"""

# Import blueprints từ các module
from app.routes.auth import auth_bp
from app.routes.coins import coins_bp
from app.routes.news import news_bp
from app.routes.watchlist import watchlist_bp

# Export tất cả blueprints
__all__ = [
    "auth_bp",
    "coins_bp",
    "news_bp",
    "watchlist_bp",
]