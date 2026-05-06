"""
News model - tin tức crypto.

Model này định nghĩa bảng news trong database:
- id: Primary key
- title: Tiêu đề tin tức
- url: Link bài viết (unique)
- source: Nguồn tin (vd: CoinDesk, Binance)
- description: Mô tả ngắn
- image_url: Ảnh thumbnail
- published_at: Thời gian đăng
- created_at: Thời gian lưu vào DB
"""

# Import db instance từ database.py (dùng chung cho tất cả models)
from app.database import db

from datetime import datetime, timezone
from typing import Optional


class News(db.Model):
    """Model News - tin tức crypto."""

    __tablename__ = "news"

    # Columns
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(255), nullable=False)
    url: str = db.Column(db.String(500), unique=True, nullable=False)
    source: str = db.Column(db.String(100))
    description: Optional[str] = db.Column(db.Text)
    image_url: Optional[str] = db.Column(db.String(500))
    published_at: datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    created_at: datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def to_dict(self) -> dict:
        """
        Serialize News thành dictionary.

        Returns:
            Dictionary chứa thông tin tin tức
        """
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "description": self.description,
            "image_url": self.image_url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<News {self.title[:30]}...>"