"""
PriceHistory model - lịch sử giá coin.

Model này định nghĩa bảng price_history trong database:
- id: Primary key
- coin_id: Foreign key tới coins.id
- price: Giá tại thời điểm
- timestamp: Thời gian ghi nhận giá

Index:
- idx_coin_timestamp: (coin_id, timestamp) để query nhanh theo coin và thời gian
"""

# Import db instance từ database.py (dùng chung cho tất cả models)
from app.database import db

from datetime import datetime, timezone


class PriceHistory(db.Model):
    """Model PriceHistory - lịch sử giá coin."""

    __tablename__ = "price_history"

    # Columns
    id: int = db.Column(db.Integer, primary_key=True)
    coin_id: str = db.Column(
        db.String(50),
        db.ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    price: float = db.Column(db.Numeric(20, 8), nullable=False)
    timestamp: datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    coin = db.relationship("Coin", back_populates="price_history")

    def to_dict(self) -> dict:
        """
        Serialize PriceHistory thành dictionary.

        Returns:
            Dictionary chứa lịch sử giá
        """
        return {
            "id": self.id,
            "coin_id": self.coin_id,
            "price": float(self.price) if self.price else 0,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

    def __repr__(self) -> str:
        return f"<PriceHistory {self.coin_id} {self.price}>"