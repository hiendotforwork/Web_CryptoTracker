# 🪙 Crypto Tracker - Tài liệu Cấu trúc Dự án

Dự án xây dựng hệ thống theo dõi thị trường tiền điện tử, cập nhật tin tức tự động và quản lý danh sách theo dõi cá nhân.

---

## 1. Kiến trúc Kỹ thuật (Tech Stack)

| Thành phần        | Công nghệ                                            | Chi tiết                                            |
| ----------------- | ---------------------------------------------------- | --------------------------------------------------- |
| Backend           | Flask                                                | Framework chính, xử lý Logic và Routes              |
| Database          | PostgreSQL (Railway)                                 | Tích hợp sẵn trên Railway                           |
| ORM               | Flask-SQLAlchemy                                     | Truy vấn database qua Object Python                 |
| Frontend          | Vue 3 + Vite                                         | Component hóa, quản 
lý state tốt hơn JS thuần       |
| Biểu đồ           | TradingView Lightweight Charts                       | Chuyên biệt cho crypto/finance, trực quan           |
| Tác vụ ngầm       | APScheduler                                          | Cập nhật dữ liệu mỗi 15-30 phút                     |
| Nguồn dữ liệu     | CoinGecko(https://api.coingecko.com/api/v3)          | Dữ liệu giá coin                                    |
|                   | Free News Crypto(https://cryptocurrency.cv/api/news) | Dữ liệu giá tin tức                                 |
| Auth              | JWT (flask-jwt-extended)                             | Không dùng session                                  |
| Trình quản lý gói | PNPM                                                 | Hạn chế dùng NPM                                    |
| Deployment        | Railway                                              | Không spin down, ~$1-2/tháng, auto deploy từ GitHub |

---

## 2. Frontend

### Yêu cầu thiết kế

- Phong cách: Responsive Web Design
- Màu sắc: #0d1a26, #1a3a5c, #3d6b8a, #8ab4c4, #e8f0f5

### Màn hình & Component

| View          | Component chính              | Chức năng                                     |
| ------------- | ---------------------------- | --------------------------------------------- |
| AuthView      | Form login/register          | Toggle giữa 2 form, lưu JWT vào localStorage  |
| HomeView      | CoinTable                    | Danh sách top coins, search, nút ➕ watchlist |
| CoinDetail    | ViewPriceChart, CompareChart | Biểu đồ TradingView, so sánh 2 coin           |
| NewsView      | NewsCard                     | Grid tin tức, search                          |
| WatchlistView | CoinTable (filtered)         | Danh sách coin đang theo dõi, nút xóa         |

---

## 3. Thiết kế cở sở dữ liệu

### Bảng users

| Tên trường    | Kiểu dữ liệu | Ràng buộc |
| ------------- | ------------ | --------- |
| id            | Serial       | PK        |
| username      | varchar      | UNIQUE    |
| email         | varchar      | UNIQUE    |
| password_hash | varchar      |           |
| created_at    | timestamp    |           |

### Bảng coins

| Tên trường  | Kiểu dữ liệu | Ràng buộc |
| ----------- | ------------ | --------- |
| id          | varchar      | PK        |
| symbol      | varchar      |           |
| name        | varchar      |           |
| image_url   | text         |           |
| last_update | timestamp    |           |

### Bảng news

| Tên trường   | Kiểu dữ liệu | Ràng buộc |
| ------------ | ------------ | --------- |
| id           | serial       | PK        |
| title        | text         |           |
| url          | text         | UNIQUE    |
| source       | varchar      |           |
| published_at | timestamp    |           |
| fectched_at  | timestamp    |           |

### Bảng watchlist

| Tên trường | Kiểu dữ liệu | Ràng buộc |
| ---------- | ------------ | --------- |
| id         | serial       | PK        |
| user_id    | serial       | FK(users) |
| coin_id    | varchar      | FK(coins) |
| added_at   | timestamp    |           |

### Bảng price_history

| Tên trường  | Kiểu dữ liệu | Ràng buộc |
| ----------- | ------------ | --------- |
| id          | Serial       | PK        |
| coin_id     | varchar      | FK(coins) |
| price_usd   | numberic     |           |
| market_cap  | numberic     |           |
| volume_24h  | numberic     |           |
| recorded_at | timestamp    | UNIQUE    |

---

## 4. API Routes

### Auth `/api/auth`

| Method | Endpoint    | Mô tả                   |
| ------ | ----------- | ----------------------- |
| POST   | `/register` | Đăng ký tài khoản       |
| POST   | `/login`    | Trả về JWT access token |

### Coins `/api/coins`

| Method | Endpoint             | Mô tả                                    |
| ------ | -------------------- | ---------------------------------------- |
| GET    | `/`                  | Danh sách coins (top 100, có phân trang) |
| GET    | `/<coin_id`          | Chi tiết 1 coin                          |
| GET    | `/<coin_id>/history` | Lịch sử giá 7 ngày gần nhất              |
| GET    | `/search?q=`         | Tìm kiếm coin theo tên/symbol            |

### News `/api/news`

| Method | Endpoint | Mô tả             |
| ------ | -------- | ----------------- |
| GET    | `/`      | Danh sách tin tức |
| GET    | `/?q=`   | Tìm kiếm tin tức  |

### Watchlist `/api/watchlist`

| Method | Endpoint    | Mô tả                            |
| ------ | ----------- | -------------------------------- |
| GET    | `/`         | Lấy danh sách coin đang theo dõi |
| POST   | `/`         | Thêm coin vào watchlist          |
| DELETE | `/<coin_id` | Xóa coin khỏi watchlist          |

---

## 5. Cấu trúc thư mục dự kiến

```
crypto-tracker/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── routes/
│   │   │   ├── auth.py          # /api/auth/*
│   │   │   ├── coins.py         # /api/coins/*
│   │   │   ├── news.py          # /api/news/*
│   │   │   └── watchlist.py     # /api/watchlist/*
│   │   ├── scheduler.py         # APScheduler jobs
│   │   └── services/
│   │       ├── coingecko.py     # Fetch giá & lịch sử
│   │       └── crypto_news.py   # Fetch tin tức
│   ├── migrations/
│   ├── config.py
│   ├── run.py
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── views/
    │   │   ├── HomeView.vue
    │   │   ├── CoinDetailView.vue
    │   │   ├── NewsView.vue
    │   │   ├── WatchlistView.vue
    │   │   └── AuthView.vue
    │   ├── components/
    │   │   ├── CoinTable.vue
    │   │   ├── PriceChart.vue
    │   │   ├── CompareChart.vue
    │   │   └── NewsCard.vue
    │   ├── stores/
    │   │   ├── auth.js
    │   │   └── watchlist.js
    │   └── router/index.js
    └── vite.config.js

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
                    └───────┬───────────┬───────────┘
                            │           │
        ┌───────────────────▼───┐   ┌───▼───────────────────┐
        │       Frontend        │   │       Frontend        │
        │ - Trang chủ           │   │ - Watchlist           │
        │ - Chi tiết coin       │   │ - Tin tức             │
        └───────────┬───────────┘   └───────────┬───────────┘
                    │                           │
        ┌───────────▼───────────┐   ┌───────────▼───────────┐
        │      Database         │   │      Database         │
        │ price_history, coins  │   │ news, watchlist       │
        └───────────────────────┘   └───────────────────────┘

---

## 7. Hướng dẫn cài đặt môi trường phát triển (Dev Setup)

### Yêu cầu tiên quyết

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** (Railway managed hoặc Local)

### Backend (Flask)

```bash
cd backend

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Khởi tạo và cập nhật Database schema
flask db upgrade

# Khởi động server
flask run
```

### Frontend (Vue 3 + Vite)

```bash
cd frontend

# Cài đặt các package
pnpm install

# Khởi động dev server
pnpm run dev
```

### Chạy kiểm thử (Testing)

```bash
# Test Backend
cd backend && pytest -v

# Test Frontend
cd frontend && pnpm run test
```
