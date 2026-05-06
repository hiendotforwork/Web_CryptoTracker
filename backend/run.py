"""
Entry point cho Crypto Tracker Backend.

Đây là file khởi động Flask server.
Chạy: python run.py

Có thể specify config bằng biến môi trường FLASK_ENV:
- FLASK_ENV=development (mặc định)
- FLASK_ENV=testing
- FLASK_ENV=production
"""

import os
from dotenv import load_dotenv

# Load biến môi trường từ .env file
load_dotenv()

# Import app sau khi load .env
from app import create_app

# Lấy config name từ biến môi trường, mặc định là development
config_name = os.environ.get("FLASK_ENV", "development")

# Tạo Flask app với config tương ứng
app = create_app(config_name)

if __name__ == "__main__":
    # Lấy port từ biến môi trường (cho Railway deployment)
    port = int(os.environ.get("PORT", 5000))
    
    # Chạy Flask development server
    app.run(
        host="0.0.0.0",
        port=port,
        debug=app.config.get("DEBUG", False)
    )