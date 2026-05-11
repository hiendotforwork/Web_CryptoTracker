# 🪙 Crypto Tracker - Tài liệu Cấu trúc Dự án

Dự án xây dựng hệ thống theo dõi thị trường tiền điện tử, cập nhật tin tức tự động và quản lý danh sách theo dõi cá nhân.

---

## 1. Kiến trúc Kỹ thuật (Tech Stack)

| Thành phần        | Công nghệ                                        | Chi tiết                                               |
| ----------------- | ------------------------------------------------ | ------------------------------------------------------ |
| Backend           | Flask                                            | Framework chính, xử lý Logic và Routes                 |
| Database          | PostgreSQL (Railway)                             | Tích hợp sẵn trên Railway                              |
| ORM               | Flask-SQLAlchemy + Flask-Migrate                 | Truy vấn database qua Object Python, migration tự động |
| Frontend          | Vue 3 + Vite                                     | Composition API, quản lý state bằng Pinia              |
| Biểu đồ           | TradingView Lightweight Charts                   | Chuyên biệt cho crypto/finance, trực quan              |
| Tác vụ ngầm       | APScheduler                                      | Cập nhật dữ liệu mỗi 15-30 phút                        |
| Nguồn dữ liệu     | CoinGecko (https://api.coingecko.com/api/v3)     | Dữ liệu giá coin                                       |
|                   | CoinDesk (https://feeds.feedburner.com/CoinDesk) | Dữ liệu tin tức                                        |
|                   | CoinTelegraph: https://cointelegraph.com/rss     | Dữ liệu tin tức                                        |
| Auth              | JWT (flask-jwt-extended)                         | Không dùng session, token lưu localStorage             |
| Rate Limiting     | Flask-Limiter                                    | Giới hạn tần suất gọi API bảo vệ server                |
| Trình quản lý gói | PNPM                                             | Hạn chế dùng NPM                                       |
| Deployment        | Railway + Docker                                 | Auto deploy từ GitHub, entrypoint chạy db migrate      |

---

## 2. Frontend

### Yêu cầu thiết kế

- Phong cách: Responsive Web Design
- Màu sắc: #0a1628, #1a3a5c, #cc2936, #e07b82, #c9a277, #ffffff, #a0b4c8, #1a3a5c, #10b981

### Màn hình & Component

| View          | Component chính              | Chức năng                                     |
| ------------- | ---------------------------- | --------------------------------------------- |
| AuthView      | Form login/register          | Toggle giữa 2 form, lưu JWT vào localStorage  |
| HomeView      | CoinTable                    | Danh sách top coins, search, nút ➕ watchlist |
| CoinDetail    | PriceChart, CompareChart     | Biểu đồ TradingView, so sánh 2 coin           |
| CompareView   | CompareChart                 | So sánh giá 2 coin bất kỳ trên 1 màn hình     |
| NewsView      | NewsCard                     | Grid tin tức, search                          |
| WatchlistView | CoinTable (filtered)         | Danh sách coin đang theo dõi, nút xóa         |
| ProfileView   | Form đổi mật khẩu / username | Quản lý tài khoản, xóa tài khoản              |
| NotFoundView  | —                            | Trang 404                                     |

---

## 3. Thiết kế cơ sở dữ liệu

### Bảng users

| Tên trường    | Kiểu dữ liệu | Ràng buộc        |
| ------------- | ------------ | ---------------- |
| id            | Integer      | PK               |
| username      | varchar(50)  | UNIQUE, NOT NULL |
| email         | varchar(120) | UNIQUE, NOT NULL |
| password_hash | varchar(256) | NOT NULL         |
| created_at    | timestamp    |                  |

### Bảng coins

| Tên trường                  | Kiểu dữ liệu  | Ràng buộc |
| --------------------------- | ------------- | --------- |
| id                          | varchar(100)  | PK        |
| name                        | varchar(255)  | NOT NULL  |
| symbol                      | varchar(20)   | NOT NULL  |
| image                       | varchar(512)  |           |
| current_price               | numeric(20,8) |           |
| market_cap                  | numeric(30,2) |           |
| market_cap_rank             | integer       |           |
| volume                      | numeric(30,2) |           |
| price_change_24h            | numeric(20,8) |           |
| price_change_percentage_24h | numeric(10,2) |           |
| circulating_supply          | numeric(30,2) |           |
| total_supply                | numeric(30,2) |           |
| ath                         | numeric(20,8) |           |
| ath_change_percentage       | numeric(10,2) |           |
| ath_date                    | timestamp     |           |
| atl                         | numeric(20,8) |           |
| atl_change_percentage       | numeric(10,2) |           |
| atl_date                    | timestamp     |           |
| last_updated                | timestamp     |           |

### Bảng news

| Tên trường   | Kiểu dữ liệu | Ràng buộc |
| ------------ | ------------ | --------- |
| id           | integer      | PK        |
| title        | varchar(255) | NOT NULL  |
| url          | varchar(500) | UNIQUE    |
| source       | varchar(100) |           |
| description  | text         |           |
| image_url    | varchar(500) |           |
| published_at | timestamp    |           |
| created_at   | timestamp    |           |

### Bảng watchlist

| Tên trường | Kiểu dữ liệu | Ràng buộc |
| ---------- | ------------ | --------- |
| id         | integer      | PK        |
| user_id    | integer      | FK(users) |
| coin_id    | varchar      | FK(coins) |
| added_at   | timestamp    |           |

### Bảng price_history

| Tên trường | Kiểu dữ liệu  | Ràng buộc |
| ---------- | ------------- | --------- |
| id         | integer       | PK        |
| coin_id    | varchar       | FK(coins) |
| price      | numeric(20,8) | NOT NULL  |
| timestamp  | timestamp     |           |

---

## 4. API Routes

### Auth `/api/auth`

| Method | Endpoint           | Auth | Mô tả                            |
| ------ | ------------------ | ---- | -------------------------------- |
| POST   | `/register`        | —    | Đăng ký tài khoản                |
| POST   | `/login`           | —    | Trả về JWT access token          |
| PATCH  | `/change-password` | JWT  | Đổi mật khẩu (yêu cầu đăng nhập) |
| PATCH  | `/change-username` | JWT  | Đổi tên đăng nhập                |
| DELETE | `/delete-account`  | JWT  | Xóa tài khoản và toàn bộ dữ liệu |

### Coins `/api/coins`

| Method | Endpoint             | Mô tả                                    |
| ------ | -------------------- | ---------------------------------------- |
| GET    | `/`                  | Danh sách coins (top 100, có phân trang) |
| GET    | `/<coin_id>`         | Chi tiết 1 coin                          |
| GET    | `/<coin_id>/history` | Lịch sử giá 7 ngày gần nhất              |
| GET    | `/search?q=`         | Tìm kiếm coin theo tên/symbol            |

### News `/api/news`

| Method | Endpoint | Mô tả             |
| ------ | -------- | ----------------- |
| GET    | `/`      | Danh sách tin tức |
| GET    | `/?q=`   | Tìm kiếm tin tức  |

### Watchlist `/api/watchlist`

| Method | Endpoint     | Auth | Mô tả                            |
| ------ | ------------ | ---- | -------------------------------- |
| GET    | `/`          | JWT  | Lấy danh sách coin đang theo dõi |
| POST   | `/`          | JWT  | Thêm coin vào watchlist          |
| DELETE | `/<coin_id>` | JWT  | Xóa coin khỏi watchlist          |

---

## 5. Cấu trúc thư mục

```
Web_CryptoTracker/
├── Dockerfile                   # Build image cho Railway
├── backend/
│   ├── entrypoint.sh            # Chạy flask db upgrade rồi gunicorn
│   ├── config.py                # Cấu hình Dev/Prod, fix DATABASE_URL
│   ├── run.py                   # Entry point Flask app
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── __init__.py          # App factory, CORS, JWT, Blueprint
│   │   ├── database.py          # SQLAlchemy instance
│   │   ├── limiter.py           # Flask-Limiter instance
│   │   ├── models/
│   │   │   ├── user.py          # Model User
│   │   │   ├── coin.py          # Model Coin
│   │   │   ├── news.py          # Model News
│   │   │   ├── watchlist.py     # Model Watchlist
│   │   │   └── price_history.py # Model PriceHistory
│   │   ├── routes/
│   │   │   ├── auth.py          # /api/auth/* (register, login, profile)
│   │   │   ├── coins.py         # /api/coins/*
│   │   │   ├── news.py          # /api/news/*
│   │   │   └── watchlist.py     # /api/watchlist/*
│   │   ├── scheduler.py         # APScheduler jobs
│   │   └── services/
│   │       ├── coingecko.py     # Fetch giá & lịch sử từ CoinGecko
│   │       └── crypto_news.py   # Fetch tin tức
│   ├── migrations/
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py         # 32 test cases auth routes
│       ├── test_coins.py
│       ├── test_watchlist.py
│       ├── test_news.py
│       ├── test_models.py
│       ├── test_services.py
│       ├── test_scheduler.py
│       └── test_db_connection.py
│
└── frontend/
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue              # Layout chính, navbar, mobile menu
        ├── assets/
        │   └── styles/
        │       └── main.css     # CSS variables (bảng màu trung tâm)
        ├── components/
        │   ├── CoinTable.vue    # Bảng danh sách coin dùng chung
        │   ├── PriceChart.vue   # Biểu đồ giá TradingView
        │   ├── CompareChart.vue # Biểu đồ so sánh 2 coin
        │   └── NewsCard.vue     # Card tin tức
        ├── views/
        │   ├── AuthView.vue         # Login / Register
        │   ├── HomeView.vue         # Trang chủ danh sách coin
        │   ├── CoinDetailView.vue   # Chi tiết coin + biểu đồ
        │   ├── CompareView.vue      # So sánh 2 coin
        │   ├── NewsView.vue         # Tin tức
        │   ├── WatchlistView.vue    # Danh sách theo dõi
        │   ├── ProfileView.vue      # Quản lý tài khoản
        │   └── NotFoundView.vue     # 404
        ├── stores/
        │   ├── auth.js          # Pinia store: user, JWT, account actions
        │   ├── coinStore.js     # Pinia store: danh sách coin
        │   └── watchlistStore.js# Pinia store: watchlist
        ├── services/
        │   └── api.js           # Axios instance, tất cả API call
        └── router/
            └── index.js         # Vue Router, route guard requiresAuth
```

---

## 6. Sơ đồ kiến trúc — Crypto Tracker

          ┌──────────────────────┐        ┌──────────────────────┐
          │   CoinGecko API      │        │ Free News Crypto API │
          │ Giá & lịch sử coin   │        │ Tin tức crypto       │
          └──────────┬───────────┘        └──────────┬───────────┘
                     │                               │
                     └──────────────┬────────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │     APScheduler       │
                        │  (15–30 phút/lần)     │
                        └───────────┬───────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │         Flask Backend         │
                    │  - Routes (REST API)          │
                    │  - Auth (JWT)                 │
                    │  - Rate Limiting              │
                    └───────┬───────────┬───────────┘
                            │           │
        ┌───────────────────▼───┐   ┌───▼───────────────────┐
        │       Frontend        │   │       Frontend        │
        │ - Trang chủ           │   │ - Watchlist           │
        │ - Chi tiết coin       │   │ - Tin tức             │
        │ - So sánh coin        │   │ - Quản lý tài khoản   │
        └───────────┬───────────┘   └───────────┬───────────┘
                    │                           │
        ┌───────────▼───────────────────────────▼───────────┐
        │                  PostgreSQL                       │
        │  users, coins, price_history, news, watchlist     │
        └───────────────────────────────────────────────────┘

---

## 7. Hướng dẫn cài đặt môi trường phát triển (Dev Setup)

### Yêu cầu tiên quyết

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** (Railway managed hoặc Local)

### Backend (Flask)

```bash
cd backend

# Tạo và kích hoạt môi trường ảo
python -m venv .venv
source .venv/bin/activate       # Linux/macOS

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Sao chép file cấu hình môi trường
cp .env.example .env            # Điền DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY

# Khởi tạo và cập nhật Database schema
flask db upgrade

# Khởi động server
flask run
```

### Frontend (Vue 3 + Vite)

```bash
# Thoát môi trường ảo Python nếu đang active
deactivate

cd frontend

# Cài đặt các package
pnpm install

# Khởi động dev server
pnpm run dev
```

### Chạy kiểm thử (Testing)

```bash
# Test Backend (kích hoạt .venv trước)
cd backend
source .venv/bin/activate
pytest -v

# Test Frontend
cd frontend && pnpm run test
```
