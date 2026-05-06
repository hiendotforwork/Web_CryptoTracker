"""
Watchlist model - coin yêu thích của user.

Model này định nghĩa bảng watchlist trong database:
- id: Primary key
- user_id: Foreign key tới users.id
- coin_id: Foreign key tới coins.id
- added_at: Thời gian thêm

Constraints:
- UniqueConstraint(user_id, coin_id): Không cho phép trùng

Relationships:
- user: Relationship tới User
- coin: Relationship tới Coin
"""

# Import db instance từ database.py (dùng chung cho tất cả models)
from app.database import db

from datetime import datetime, timezone


class Watchlist(db.Model):
    """Model Watchlist - coin yêu thích của user."""

    __tablename__ = "watchlist"
    __table_args__ = (
        # Unique constraint: không cho phép trùng user_id + coin_id
        db.UniqueConstraint("user_id", "coin_id", name="uix_user_coin"),
    )

    # Columns
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    coin_id: str = db.Column(
        db.String(50),
        db.ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=False
    )
    added_at: datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user = db.relationship("User", back_populates="watchlist_items")
    coin = db.relationship("Coin", back_populates="watchlist_items")

    def to_dict(self) -> dict:
        """
        Serialize Watchlist thành dictionary.

        Returns:
            Dictionary chứa thông tin watchlist và thông tin coin
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "coin_id": self.coin_id,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "coin": self.coin.to_dict() if self.coin else None
        }

    def __repr__(self) -> str:
        return f"<Watchlist user={self.user_id} coin={self.coin_id}>"