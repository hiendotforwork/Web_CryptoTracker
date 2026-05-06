"""
Coin model - thông tin coin từ CoinGecko.

Model này định nghĩa bảng coins trong database:
- id: Primary key (coin id từ CoinGecko, vd: bitcoin)
- name: Tên đầy đủ của coin
- symbol: Viết tắt (viết thường, vd: btc)
- image: URL ảnh
- current_price: Giá hiện tại (USD)
- market_cap: Vốn hóa thị trường
- market_cap_rank: Thứ hạng theo vốn hóa
- volume: Khối lượng giao dịch 24h
- price_change_24h: Thay đổi giá 24h
- price_change_percentage_24h: % thay đổi 24h
- circulating_supply: Lượng cung lưu hành
- total_supply: Tổng cung
- ath: All-time high
- ath_change_percentage: % thay đổi từ ATH
- ath_date: Ngày ATH
- atl: All-time low
- atl_change_percentage: % thay đổi từ ATL
- atl_date: Ngày ATL
- last_updated: Thời gian cập nhật cuối
"""

# Import db instance từ database.py (dùng chung cho tất cả models)
from app.database import db

from datetime import datetime, timezone


class Coin(db.Model):
    """Model Coin - thông tin coin từ CoinGecko."""

    __tablename__ = "coins"

    # Columns
    id: str = db.Column(db.String(50), primary_key=True)  # coin id từ CoinGecko (vd: bitcoin)
    name: str = db.Column(db.String(100), nullable=False, index=True)
    symbol: str = db.Column(db.String(20), nullable=False, index=True)  # viết thường (vd: btc)
    image: str = db.Column(db.String(255))
    current_price: float = db.Column(db.Numeric(20, 8), default=0)
    market_cap: float = db.Column(db.Numeric(30, 2), default=0)
    market_cap_rank: int = db.Column(db.Integer)
    volume: float = db.Column(db.Numeric(30, 2), default=0)
    price_change_24h: float = db.Column(db.Numeric(20, 8), default=0)
    price_change_percentage_24h: float = db.Column(db.Numeric(10, 2), default=0)
    circulating_supply: float = db.Column(db.Numeric(30, 2))
    total_supply: float = db.Column(db.Numeric(30, 2))
    ath: float = db.Column(db.Numeric(20, 8))
    ath_change_percentage: float = db.Column(db.Numeric(10, 2))
    ath_date: datetime = db.Column(db.DateTime(timezone=True))
    atl: float = db.Column(db.Numeric(20, 8))
    atl_change_percentage: float = db.Column(db.Numeric(10, 2))
    atl_date: datetime = db.Column(db.DateTime(timezone=True))
    last_updated: datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    watchlist_items = db.relationship("Watchlist", back_populates="coin", lazy="dynamic")
    price_history = db.relationship(
        "PriceHistory",
        back_populates="coin",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    def to_dict(self) -> dict:
        """
        Serialize Coin thành dictionary.

        Returns:
            Dictionary chứa thông tin coin
        """
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "image": self.image,
            "current_price": float(self.current_price) if self.current_price else 0,
            "market_cap": float(self.market_cap) if self.market_cap else 0,
            "market_cap_rank": self.market_cap_rank,
            "volume": float(self.volume) if self.volume else 0,
            "price_change_24h": float(self.price_change_24h) if self.price_change_24h else 0,
            "price_change_percentage_24h": float(self.price_change_percentage_24h) if self.price_change_percentage_24h else 0,
            "circulating_supply": float(self.circulating_supply) if self.circulating_supply else 0,
            "total_supply": float(self.total_supply) if self.total_supply else 0,
            "ath": float(self.ath) if self.ath else 0,
            "ath_change_percentage": float(self.ath_change_percentage) if self.ath_change_percentage else 0,
            "ath_date": self.ath_date.isoformat() if self.ath_date else None,
            "atl": float(self.atl) if self.atl else 0,
            "atl_change_percentage": float(self.atl_change_percentage) if self.atl_change_percentage else 0,
            "atl_date": self.atl_date.isoformat() if self.atl_date else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }

    def __repr__(self) -> str:
        return f"<Coin {self.symbol}>"