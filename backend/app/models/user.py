"""
User model - người dùng đăng ký.

Model này định nghĩa bảng users trong database:
- id: Primary key
- username: Tên đăng nhập (unique, index)
- email: Email (unique, index)
- password_hash: Hash của mật khẩu
- created_at: Thời gian tạo

Methods:
- set_password(): Thiết lập password với hashing
- check_password(): Kiểm tra password có khớp không
- to_dict(): Serialize thành dictionary (KHÔNG chứa password_hash)
"""

# Import db instance từ database.py (dùng chung cho tất cả models)
from app.database import db

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """Model User - người dùng đăng ký."""

    __tablename__ = "users"

    # Columns
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email: str = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash: str = db.Column(db.String(256), nullable=False)
    created_at: datetime = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    watchlist_items = db.relationship(
        "Watchlist",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    def set_password(self, password: str) -> None:
        """
        Thiết lập password với hashing.

        Args:
            password: Plain text password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Kiểm tra password có khớp không.

        Args:
            password: Plain text password cần kiểm tra

        Returns:
            True nếu khớp, False nếu không
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """
        Serialize User thành dictionary.

        LƯU Ý: KHÔNG trả password_hash vì lý do bảo mật.

        Returns:
            Dictionary chứa id, username, email, created_at
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<User {self.username}>"