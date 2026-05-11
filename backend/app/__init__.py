"""
App Factory module cho Crypto Tracker Backend.

Module này khởi tạo Flask app với các extensions:
- Flask-SQLAlchemy: ORM database
- Flask-JWT-Extended: Authentication JWT
- Flask-CORS: Cross-origin resource sharing
- Flask-Migrate: Database migrations

Sử dụng App Factory pattern với hàm create_app(config_name) để trả về app instance.
"""

import logging
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

# Import db từ models package (dùng chung cho tất cả models)
from app.models import db

# Import limiter từ module limiter
from app.limiter import limiter

# Khởi tạo các extensions
jwt = JWTManager()
migrate = Migrate()
logger = logging.getLogger(__name__)


def create_app(config_name: str = "development"):
    """
    Hàm Factory tạo Flask app với cấu hình được chỉ định.

    Args:
        config_name: Tên cấu hình ('development', 'testing', 'production')
                  Mặc định là 'development'

    Returns:
        Flask app instance đã được cấu hình đầy đủ
    """
    # Import config ở đây để tránh circular import
    from config import config_by_name
    import os

    # Lấy class config tương ứng
    config_class = config_by_name.get(config_name, config_by_name["default"])

    # Đường dẫn tới thư mục build của Vue (frontend/dist)
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

    # Tạo Flask app có phục vụ file tĩnh từ frontend/dist
    app = Flask(__name__, static_folder=frontend_dist, static_url_path="/")
    app.config.from_object(config_class)

    # Thiết lập logging
    _setup_logging(app)

    # Khởi tạo extensions với app
    _init_extensions(app)

    # Đăng ký routes
    _register_routes(app)

    # Khởi động scheduler (chỉ khi không phải testing)
    _init_scheduler(app)

    # Đăng ký error handlers
    _register_error_handlers(app)

    logger.info(f"Crypto Tracker API đã khởi động với cấu hình: {config_name}")

    return app


def _setup_logging(app: Flask):
    """Thiết lập logging cho ứng dụng."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s trong %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Log cấp độ warning từ sqlalchemy
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def _init_extensions(app: Flask):
    """Khởi tạo và đăng ký các extensions với Flask app."""
    # SQLAlchemy
    db.init_app(app)

    # JWT
    jwt.init_app(app)

    # CORS — production: nếu không set CORS_ORIGINS, mặc định "*" vì
    # frontend được serve cùng origin qua Flask static. Không để "" (empty)
    # vì Flask-CORS sẽ block tất cả cross-origin requests.
    if app.config.get("DEBUG"):
        cors_origins = "*"
    else:
        cors_origins = app.config.get("CORS_ORIGINS", "*")
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # Limiter
    limiter.init_app(app)

    # Migrate
    migrate.init_app(app, db)


def _register_routes(app: Flask):
    """Đăng ký các blueprints/routes cho ứng dụng."""
    from app.routes import auth_bp, coins_bp, news_bp, watchlist_bp
    import os

    # Route serve Vue SPA (Catch-all route)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_vue(path):
        """Phục vụ file tĩnh của Vue SPA hoặc index.html cho các route không phải API."""
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return app.send_static_file(path)
        return app.send_static_file('index.html')

    # Đăng ký blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(coins_bp, url_prefix="/api/coins")
    app.register_blueprint(news_bp, url_prefix="/api/news")
    app.register_blueprint(watchlist_bp, url_prefix="/api/watchlist")


def _init_scheduler(app: Flask):
    """Khởi động APScheduler (chỉ khi không phải testing)."""
    from app.scheduler import init_scheduler
    init_scheduler(app)


def _register_error_handlers(app: Flask):
    """Đăng ký các error handlers cho ứng dụng."""

    @app.errorhandler(404)
    def not_found(error):
        """Xử lý lỗi 404 - Not Found."""
        return jsonify({"error": "Không tìm thấy resource"}), 404

    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Xử lý lỗi 429 - Too Many Requests."""
        return jsonify({"error": f"Quá nhiều yêu cầu: {e.description}"}), 429

    @app.errorhandler(500)
    def internal_error(error):
        """Xử lý lỗi 500 - Internal Server Error."""
        logger.error(f"Lỗi server nội bộ: {error}")
        return jsonify({"error": "Đã có lỗi xảy ra ở server"}), 500

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Xử lý khi JWT token hết hạn."""
        return jsonify({
            "error": "Token đã hết hạn, vui lòng đăng nhập lại"
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Xử lý khi JWT token không hợp lệ."""
        return jsonify({"error": "Token không hợp lệ"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Xử lý khi thiếu JWT token."""
        return jsonify({"error": "Thiếu token xác thực"}), 401