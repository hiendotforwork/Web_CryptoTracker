"""
Test Scheduler - Unit tests cho APScheduler Configuration.

Task 5.1 - APScheduler Configuration:
1. init_scheduler bị bypass trong môi trường testing
2. Scheduler khởi động đúng với 2 jobs (có replace_existing + atexit)   [FIX]
3. Job update_coins gọi fetch_and_save_coins
4. Job update_news gọi fetch_and_save_news
5. Job xử lý exception không crash

CHANGES
- test_scheduler_startup_with_two_jobs: dùng mock_app TESTING=False (fix bug)
- Bổ sung assert replace_existing=True cho từng job
- Bổ sung assert atexit.register được gọi
- Bổ sung assert interval đúng (30 phút / 15 phút)
"""

import sys
from unittest.mock import MagicMock, patch, call

import pytest


# =====================================================
# MOCK MODULE TRƯỚC KHI IMPORT
# crypto_coingecko chưa tồn tại dưới dạng file riêng → mock để ngăn ImportError
# khi app.scheduler được load (nó import from app.services.crypto_coingecko).
# KHÔNG mock crypto_news vì module đó đã tồn tại thật.
# =====================================================

# =====================================================
# IMPORTS
# app.services.crypto_coingecko đã được mock ở conftest.py
# =====================================================

from app import create_app
from app.database import db


# =====================================================
# FIXTURES
# =====================================================

@pytest.fixture
def app():
    """
    Override conftest app fixture để thêm scheduler cleanup sau mỗi test.
    Cần reset scheduler_instance để tránh state rò rỉ giữa các test.
    """
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    from app import scheduler as scheduler_module
    scheduler_module.scheduler_instance = None


@pytest.fixture(autouse=True)
def reset_scheduler():
    """Reset scheduler state trước và sau mỗi test."""
    from app import scheduler as scheduler_module
    scheduler_module.scheduler_instance = None
    yield
    scheduler_module.scheduler_instance = None


@pytest.fixture
def sample_coins(app):
    from app.models import Coin
    with app.app_context():
        coins = [
            Coin(id="bitcoin",  name="Bitcoin",  symbol="btc", current_price=42000),
            Coin(id="ethereum", name="Ethereum", symbol="eth", current_price=2500),
        ]
        db.session.add_all(coins)
        db.session.commit()


# =====================================================
# TEST CLASS
# =====================================================

class TestScheduler:

    # --------------------------------------------------
    # Test #1: bypass trong testing
    # --------------------------------------------------

    def test_init_scheduler_bypass_in_testing(self, app):
        """
        Test #1: TESTING=True → scheduler không khởi động.
        Gọi init_scheduler → scheduler_instance vẫn là None.
        """
        from app import scheduler as scheduler_module
        scheduler_module.init_scheduler(app)
        assert scheduler_module.scheduler_instance is None, \
            "Scheduler không được khởi động trong môi trường testing"

    # --------------------------------------------------
    # Test #2: khởi động đúng với 2 jobs — ĐÃ FIX BUG + BỔ SUNG ASSERTION
    # --------------------------------------------------

    def test_scheduler_startup_with_two_jobs(self, app):
        """
        Test #2: Dùng mock_app với TESTING=False để bypass check, sau đó verify:
        - BackgroundScheduler được tạo
        - 2 jobs được thêm với id đúng
        - replace_existing=True trên từng job (tránh trùng khi hot-reload)
        - Interval đúng: update_coins=30 phút, update_news=15 phút
        - scheduler.start() được gọi
        - atexit.register được gọi để shutdown sạch

        BUG ĐÃ FIX: version cũ dùng testing app nên init_scheduler bypass sớm,
        mock không bao giờ được gọi → test luôn FAIL.
        """
        from app import scheduler as scheduler_module

        with patch('app.scheduler.BackgroundScheduler') as MockScheduler, \
             patch('atexit.register') as mock_atexit_register:

            mock_scheduler = MagicMock()
            MockScheduler.return_value = mock_scheduler

            # QUAN TRỌNG: mock_app với TESTING=False
            mock_app = MagicMock()
            mock_app.config = {"TESTING": False}

            scheduler_module.init_scheduler(mock_app)

            # --- BackgroundScheduler được khởi tạo ---
            MockScheduler.assert_called_once()

            # --- Đúng 2 jobs ---
            assert mock_scheduler.add_job.call_count == 2, \
                f"Phải có 2 jobs, thực tế có {mock_scheduler.add_job.call_count}"

            call_args_list = mock_scheduler.add_job.call_args_list
            job_kwargs = {c.kwargs.get('id'): c.kwargs for c in call_args_list}

            assert 'update_coins' in job_kwargs, "Job update_coins phải được thêm"
            assert 'update_news'  in job_kwargs, "Job update_news phải được thêm"

            # --- replace_existing=True trên từng job ---
            for job_id, kwargs in job_kwargs.items():
                assert kwargs.get('replace_existing') is True, \
                    f"Job '{job_id}' phải có replace_existing=True (tránh trùng khi hot-reload)"

            # --- Interval đúng theo PLAN (minutes) ---
            # Kiểm tra unconditional — bắt buộc phải có, không được bỏ qua
            coins_kwargs = job_kwargs['update_coins']
            news_kwargs = job_kwargs['update_news']

            coins_minutes = coins_kwargs.get('minutes') or \
                            coins_kwargs.get('trigger_args', {}).get('minutes')
            news_minutes = news_kwargs.get('minutes') or \
                           news_kwargs.get('trigger_args', {}).get('minutes')

            assert coins_minutes == 30, \
                f"Job update_coins phải chạy mỗi 30 phút, thực tế: {coins_minutes}"
            assert news_minutes == 15, \
                f"Job update_news phải chạy mỗi 15 phút, thực tế: {news_minutes}"

            # --- scheduler.start() ---
            mock_scheduler.start.assert_called_once()

            # --- atexit.register được gọi để shutdown sạch ---
            # LƯU Ý: dùng assert riêng biệt, không ghép với chuỗi message bằng dấu phẩy
            # (vì "mock.assert_called_once(), 'msg'" tạo tuple, message không bao giờ hiển thị)
            mock_atexit_register.assert_called_once()
            assert mock_atexit_register.call_count == 1, \
                "atexit.register phải được gọi đúng 1 lần để scheduler shutdown sạch"

    # --------------------------------------------------
    # Test #3: update_coins gọi đúng service
    # --------------------------------------------------

    def test_job_update_coins_calls_fetch_and_save_coins(self, app):
        """
        Test #3: _job_update_coins → fetch_and_save_coins() được gọi 1 lần.
        Patch tại vị trí import trong scheduler module (không patch mock object).
        """
        from app import scheduler as scheduler_module

        with patch('app.scheduler.fetch_and_save_coins', return_value=5) as mock_fetch:
            scheduler_module._job_update_coins(app)
            mock_fetch.assert_called_once()

    # --------------------------------------------------
    # Test #4: update_news gọi đúng service
    # --------------------------------------------------

    def test_job_update_news_calls_fetch_and_save_news(self, app):
        """
        Test #4: _job_update_news → fetch_and_save_news() được gọi 1 lần.
        """
        from app import scheduler as scheduler_module

        with patch('app.scheduler.fetch_and_save_news', return_value=3) as mock_fetch:
            scheduler_module._job_update_news(app)
            mock_fetch.assert_called_once()

    # --------------------------------------------------
    # Test #5: exception không crash server
    # --------------------------------------------------

    def test_job_handles_exception_without_crash(self, app):
        """
        Test #5: Khi service raise exception, job bắt lại — server không crash.
        """
        from app import scheduler as scheduler_module

        # coins job
        with patch('app.scheduler.fetch_and_save_coins', side_effect=Exception("Network error")):
            try:
                scheduler_module._job_update_coins(app)
            except Exception:
                pytest.fail("_job_update_coins không được raise exception ra ngoài")

        # news job
        with patch('app.scheduler.fetch_and_save_news', side_effect=Exception("API timeout")):
            try:
                scheduler_module._job_update_news(app)
            except Exception:
                pytest.fail("_job_update_news không được raise exception ra ngoài")

    # --------------------------------------------------
    # Test bổ sung: zero results
    # --------------------------------------------------

    def test_job_handles_zero_results(self, app):
        """Trả về 0 (không có data mới) → không raise exception."""
        from app import scheduler as scheduler_module

        with patch('app.scheduler.fetch_and_save_coins', return_value=0):
            try:
                scheduler_module._job_update_coins(app)
            except Exception as e:
                pytest.fail(f"Exception khi count=0 (coins): {e}")

        with patch('app.scheduler.fetch_and_save_news', return_value=0):
            try:
                scheduler_module._job_update_news(app)
            except Exception as e:
                pytest.fail(f"Exception khi count=0 (news): {e}")


# =====================================================
# INTEGRATION TESTS
# =====================================================

class TestSchedulerIntegration:

    def test_app_does_not_start_scheduler_in_testing(self, app):
        """Integration: create_app("testing") → scheduler_instance là None."""
        from app import scheduler as scheduler_module
        assert scheduler_module.scheduler_instance is None, \
            f"App testing không được start scheduler, nhưng có: {scheduler_module.scheduler_instance}"

    def test_scheduler_with_real_database(self, app, sample_coins):
        """Job chạy trong app_context, database vẫn accessible sau khi job kết thúc."""
        from app import scheduler as scheduler_module
        from app.models import Coin

        with patch('app.scheduler.fetch_and_save_coins', return_value=1) as mock_fetch:
            with app.app_context():
                scheduler_module._job_update_coins(app)

            mock_fetch.assert_called_once()

            with app.app_context():
                assert len(Coin.query.all()) == 2