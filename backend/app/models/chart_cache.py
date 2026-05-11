"""
ChartCache model - Cache lịch sử giá coin từ CoinGecko.

WHY: CoinGecko free plan giới hạn 15 calls/phút.
     Mỗi lần xem biểu đồ hoặc so sánh coins đều gọi API trực tiếp → nhanh chạm limit.
HOW: Lưu kết quả API vào bảng này, kèm thời điểm cache.
     Khi request đến, kiểm tra cache còn fresh không (theo TTL per period).
     Nếu fresh → trả từ DB, không gọi API.
     Nếu stale / chưa có → gọi API rồi upsert cache.
     Nếu API fail → trả stale cache (graceful degradation).

TTL policy:
    days=1  → 5 phút
    days=7  → 15 phút
    days=30 → 30 phút
    days=90 → 60 phút
"""

from datetime import datetime, timezone
from app.database import db


class ChartCache(db.Model):
    """Model ChartCache - cache lịch sử giá coin theo period."""

    __tablename__ = "chart_cache"

    # Columns
    id: int = db.Column(db.Integer, primary_key=True)
    coin_id: str = db.Column(
        db.String(100),
        db.ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Số ngày period: 1, 7, 30, 90
    days: int = db.Column(db.Integer, nullable=False)
    # JSON string: [[timestamp_ms, price], ...]
    prices_json: str = db.Column(db.Text, nullable=False)
    cached_at: datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Mỗi cặp (coin_id, days) chỉ có 1 cache entry
    __table_args__ = (
        db.UniqueConstraint("coin_id", "days", name="uq_chart_cache_coin_days"),
    )

    # Relationship
    coin = db.relationship("Coin", backref=db.backref("chart_caches", lazy="dynamic"))

    def to_dict(self) -> dict:
        """Serialize ChartCache thành dictionary."""
        return {
            "id": self.id,
            "coin_id": self.coin_id,
            "days": self.days,
            "cached_at": self.cached_at.isoformat() if self.cached_at else None,
        }

    def __repr__(self) -> str:
        return f"<ChartCache {self.coin_id} {self.days}d>"
