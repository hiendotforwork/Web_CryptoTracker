"""
Models package - Export all models.

Module này export tất cả models và db instance để import dễ dàng hơn.

Ví dụ sử dụng:
    from app.models import User, Coin, News, Watchlist, PriceHistory, ChartCache
    from app.models import db
"""

from app.database import db
from app.models.user import User
from app.models.coin import Coin
from app.models.news import News
from app.models.watchlist import Watchlist
from app.models.price_history import PriceHistory
from app.models.chart_cache import ChartCache

# Export tất cả models và db
__all__ = [
    "db",
    "User",
    "Coin",
    "News",
    "Watchlist",
    "PriceHistory",
    "ChartCache",
]