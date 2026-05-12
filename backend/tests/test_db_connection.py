"""
Script kiểm tra kết nối Database.

What: Thử kết nối tới PostgreSQL và kiểm tra sự tồn tại của các bảng.
Why: Để đảm bảo cấu hình .env chính xác và database đang hoạt động.
How: Sử dụng Flask app context và SQLAlchemy engine.
"""

import os
import sys
from sqlalchemy import text

# Thêm thư mục hiện tại vào path để import được app
sys.path.append(os.getcwd())

try:
    from app import create_app
    from app.database import db
    from dotenv import load_dotenv

    # Load biến môi trường
    load_dotenv()

    # Tạo app instance với cấu hình development
    app = create_app("development")

    print("--- Đang bắt đầu kiểm tra kết nối Database ---")
    
    with app.app_context():
        # 1. Thử thực hiện một truy vấn đơn giản
        try:
            db.session.execute(text("SELECT 1"))
            print("✅ Kết nối cơ bản tới PostgreSQL: THÀNH CÔNG")
        except Exception as e:
            print(f"❌ Lỗi kết nối tới PostgreSQL: {e}")
            sys.exit(1)

        # 2. Kiểm tra các bảng quan trọng
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ["users", "coins", "watchlist", "news", "chart_cache"]
        print(f"\nDanh sách các bảng hiện có: {tables}")
        
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if not missing_tables:
            print("✅ Tất cả các bảng quan trọng đều đã tồn tại.")
        else:
            print(f"⚠️ Thiếu các bảng: {missing_tables}")
            print("👉 Gợi ý: Hãy chạy lệnh 'flask db upgrade' để tạo các bảng.")

    print("\n--- Kiểm tra hoàn tất ---")

except ImportError as e:
    print(f"❌ Lỗi: Không thể import các module cần thiết. Hãy đảm bảo bạn đã cài đặt đủ requirements.txt.")
    print(f"Chi tiết lỗi: {e}")
except Exception as e:
    print(f"❌ Đã xảy ra lỗi không xác định: {e}")
