"""
APScheduler configuration module.

Quản lý các tác vụ ngầm:
- update_coins: Cập nhật giá coins + lưu price history — mỗi 30 phút
- update_news: Lưu tin tức mới — mỗi 15 phút

Chỉ khởi chạy khi config_name != 'testing'.
"""

import atexit
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from app.services.crypto_coingecko import fetch_and_save_coins
from app.services.crypto_news import fetch_and_save_news

logger = logging.getLogger(__name__)

# Biến toàn cục lưu scheduler instance
scheduler_instance: BackgroundScheduler | None = None


def init_scheduler(app):
    """
    Khởi tạo và cấu hình APScheduler.

    Args:
        app: Flask app instance
    """
    global scheduler_instance

    # Chỉ khởi chạy khi không phải testing
    if app.config.get("TESTING"):
        logger.info("[Scheduler] Bỏ qua khởi động vì cấu hình testing")
        return

    # Tạo scheduler instance
    scheduler = BackgroundScheduler()
    scheduler_instance = scheduler

    # Job: Cập nhật coins mỗi 30 phút
    scheduler.add_job(
        func=_job_update_coins,
        trigger="interval",
        minutes=30,
        id="update_coins",
        replace_existing=True,
        kwargs={"app": app},
    )

    # Job: Cập nhật news mỗi 15 phút
    scheduler.add_job(
        func=_job_update_news,
        trigger="interval",
        minutes=15,
        id="update_news",
        replace_existing=True,
        kwargs={"app": app},
    )

    # Khởi chạy scheduler
    scheduler.start()
    logger.info("[Scheduler] Đã khởi động với 2 jobs")

    # Đăng ký atexit để dừng sạch khi server tắt
    atexit.register(lambda: _shutdown_scheduler())


def _shutdown_scheduler():
    """Dừng scheduler instance."""
    global scheduler_instance

    if scheduler_instance is not None:
        scheduler_instance.shutdown(wait=False)
        logger.info("[Scheduler] Đã dừng")


def _job_update_coins(app):
    """
    Job: Cập nhật coins và lưu price history.

    Args:
        app: Flask app instance
    """
    with app.app_context():
        try:
            count = fetch_and_save_coins()
            if count > 0:
                logger.info(f"[Scheduler] Đã cập nhật {count} coins, thêm {count} price records")
            else:
                logger.info("[Scheduler] Không có coins mới để cập nhật")
        except Exception as e:
            logger.error(f"[Scheduler] Lỗi khi cập nhật coins: {e}")


def _job_update_news(app):
    """
    Job: Lưu tin tức mới.

    Args:
        app: Flask app instance
    """
    with app.app_context():
        try:
            count = fetch_and_save_news()
            if count > 0:
                logger.info(f"[Scheduler] Đã lưu {count} tin mới")
            else:
                logger.info("[Scheduler] Không có tin mới để lưu")
        except Exception as e:
            logger.error(f"[Scheduler] Lỗi khi cập nhật news: {e}")