"""
Coins routes module.

Định nghĩa các routes cho coins:
- GET /api/coins/: Danh sách coins có phân trang
- GET /api/coins/<coin_id>: Chi tiết một coin
- GET /api/coins/search: Tìm kiếm coins
- GET /api/coins/<coin_id>/history: Lịch sử giá
"""

from flask import Blueprint, request, jsonify
from app.models import Coin, PriceHistory
from app.services.coingecko import (
    fetch_top_coins,
    fetch_coin_detail,
    fetch_coin_history
)

# Khởi tạo Blueprint
coins_bp = Blueprint("coins", __name__)

# Cấu hình phân trang
COINS_PER_PAGE = 25


@coins_bp.route("/", methods=["GET"])
def get_coins():
    """
    Lấy danh sách coins có phân trang.

    Query params:
        - page (int): Số trang, mặc định 1

    Returns:
        HTTP 200: {'coins': [...], 'page': 1, 'per_page': 25, 'total': ..., 'total_pages': ...}
    """
    page = request.args.get("page", 1, type=int)
    per_page = COINS_PER_PAGE

    # Query từ DB trước
    query = Coin.query.order_by(Coin.market_cap_rank.asc().nullslast())

    # Tính tổng số coins
    total = query.count()
    total_pages = (total + per_page - 1) // per_page

    # Nếu DB trống, gọi API lấy dữ liệu
    if total == 0:
        coins_data = fetch_top_coins(page, per_page)
        if coins_data:
            for coin_data in coins_data:
                _upsert_coin(coin_data)
            # Query lại sau khi upsert
            query = Coin.query.order_by(Coin.market_cap_rank.asc().nullslast())
            total = query.count()
            total_pages = (total + per_page - 1) // per_page

    # Lấy dữ liệu trang hiện tại
    coins = query.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "coins": [coin.to_dict() for coin in coins],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages
    })


@coins_bp.route("/search", methods=["GET"])
def search_coins():
    """
    Tìm kiếm coins theo tên hoặc symbol.

    Query params:
        - q (str): Từ khóa tìm kiếm

    Returns:
        HTTP 200: {'coins': [...]}
        HTTP 400: {'error': 'Tham số q không được để trống'}
    """
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Tham số q không được để trống"}), 400

    # Tìm kiếm case-insensitive trong name và symbol
    coins = Coin.query.filter(
        (Coin.name.ilike(f"%{query}%")) |
        (Coin.symbol.ilike(f"%{query}%"))
    ).limit(20).all()

    # Nếu không có trong DB, gọi API
    if not coins:
        # TODO: Gọi CoinGecko search API
        pass

    return jsonify({
        "coins": [coin.to_dict() for coin in coins]
    })


@coins_bp.route("/<coin_id>", methods=["GET"])
def get_coin_detail(coin_id: str):
    """
    Lấy chi tiết một coin.

    Args:
        coin_id: ID của coin (vd: bitcoin, ethereum)

    Returns:
        HTTP 200: {'coin': {...}}
        HTTP 404: {'error': 'Không tìm thấy coin: ...'}
        HTTP 503: {'error': 'Không thể lấy dữ liệu từ API'}
    """
    # Query từ DB trước
    coin = Coin.query.get(coin_id)

    if not coin:
        # Gọi API lấy mới
        coin_data = fetch_coin_detail(coin_id)
        if coin_data:
            coin = _upsert_coin(coin_data)
        else:
            return jsonify({"error": f"Không tìm thấy coin: {coin_id}"}), 404

    return jsonify({"coin": coin.to_dict()})


@coins_bp.route("/<coin_id>/history", methods=["GET"])
def get_coin_history(coin_id: str):
    """
    Lấy lịch sử giá của một coin.

    Args:
        coin_id: ID của coin

    Query params:
        - days (int): Số ngày, mặc định 7

    Returns:
        HTTP 200: {'prices': [[timestamp, price], ...]}
        HTTP 404: {'error': 'Không tìm thấy coin'}
    """
    days = request.args.get("days", 7, type=int)

    # Kiểm tra coin tồn tại
    coin = Coin.query.get(coin_id)
    if not coin:
        # Thử fetch từ API
        coin_data = fetch_coin_detail(coin_id)
        if not coin_data:
            return jsonify({"error": f"Không tìm thấy coin: {coin_id}"}), 404
        coin = _upsert_coin(coin_data)

    # Gọi API lấy lịch sử giá
    history_data = fetch_coin_history(coin_id, days)

    if history_data and history_data.get("prices"):
        prices = [
            [price[0], price[1]]  # [timestamp_ms, price]
            for price in history_data["prices"]
        ]
    else:
        # Fallback: Lấy từ DB
        price_records = PriceHistory.query.filter(
            PriceHistory.coin_id == coin_id
        ).order_by(PriceHistory.timestamp.asc()).all()
        prices = [
            [
                int(record.timestamp.timestamp() * 1000),
                float(record.price)
            ]
            for record in price_records
        ]

    return jsonify({"prices": prices})


def _upsert_coin(coin_data: dict) -> Coin:
    """
    Upsert coin vào DB.

    Args:
        coin_data: Dictionary chứa thông tin coin từ CoinGecko

    Returns:
        Coin instance đã được lưu
    """
    coin_id = coin_data.get("id")
    coin = Coin.query.get(coin_id)

    if coin:
        # Cập nhật
        coin.name = coin_data.get("name", coin.name)
        coin.symbol = coin_data.get("symbol", coin.symbol).lower()
        coin.image = coin_data.get("image", coin.image)
        coin.current_price = coin_data.get("current_price", coin.current_price)
        coin.market_cap = coin_data.get("market_cap", coin.market_cap)
        coin.market_cap_rank = coin_data.get("market_cap_rank", coin.market_cap_rank)
        coin.volume = coin_data.get("total_volume", coin.volume)
        coin.price_change_24h = coin_data.get("price_change_24h", coin.price_change_24h)
        coin.price_change_percentage_24h = coin_data.get(
            "price_change_percentage_24h", coin.price_change_percentage_24h
        )
        coin.circulating_supply = coin_data.get("circulating_supply", coin.circulating_supply)
        coin.total_supply = coin_data.get("total_supply", coin.total_supply)

        # ATH/ATL
        market_data = coin_data.get("market_data", {})
        coin.ath = market_data.get("ath", {}).get("usd", coin.ath)
        coin.ath_change_percentage = market_data.get("ath_change_percentage", {}).get("usd", coin.ath_change_percentage)
        coin.ath_date = market_data.get("ath_date", {}).get("usd", coin.ath_date)
        coin.atl = market_data.get("atl", {}).get("usd", coin.atl)
        coin.atl_change_percentage = market_data.get("atl_change_percentage", {}).get("usd", coin.atl_change_percentage)
        coin.atl_date = market_data.get("atl_date", {}).get("usd", coin.atl_date)
    else:
        # Tạo mới
        market_data = coin_data.get("market_data", {})
        coin = Coin(
            id=coin_id,
            name=coin_data.get("name"),
            symbol=coin_data.get("symbol", "").lower(),
            image=coin_data.get("image"),
            current_price=coin_data.get("current_price", 0),
            market_cap=coin_data.get("market_cap", 0),
            market_cap_rank=coin_data.get("market_cap_rank"),
            volume=coin_data.get("total_volume", 0),
            price_change_24h=coin_data.get("price_change_24h", 0),
            price_change_percentage_24h=coin_data.get("price_change_percentage_24h", 0),
            circulating_supply=coin_data.get("circulating_supply"),
            total_supply=coin_data.get("total supply"),
            ath=market_data.get("ath", {}).get("usd"),
            ath_change_percentage=market_data.get("ath_change_percentage", {}).get("usd"),
            ath_date=market_data.get("ath_date", {}).get("usd"),
            atl=market_data.get("atl", {}).get("usd"),
            atl_change_percentage=market_data.get("atl_change_percentage", {}).get("usd"),
            atl_date=market_data.get("atl_date", {}).get("usd")
        )

    # Import db từ models package
    from app.models import db
    db.session.add(coin)
    db.session.commit()

    return coin