# 🪙 Crypto Tracker — Kế hoạch Phát triển Chi tiết

> **Tech Stack**: Flask + Vue 3 + Vite + PostgreSQL + JWT + APScheduler
> **Môi trường**: Python 3.12.3 | Node v22.22.2 | PostgreSQL local (dev) → Railway (prod)
> **Package Manager**: `pnpm` (frontend) | `pip` trong `.venv` (backend)
> **Testing**: Manual + Unit test cơ bản (pytest, vitest)

---

## ⚠️ Quy tắc Môi trường Bắt buộc (AI phải tuân thủ)

> [!IMPORTANT]
> **Quy tắc tách biệt môi trường**: Backend Python và Frontend Node.js **KHÔNG được chạy lẫn môi trường**.

### Khi làm việc với Backend
```bash
# Kích hoạt môi trường ảo Python TRƯỚC KHI chạy bất kỳ lệnh Flask/pip nào
cd backend
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Kiểm tra môi trường đúng chưa (phải thấy đường dẫn .venv)
which python   # → .../backend/.venv/bin/python
```

### Khi làm việc với Frontend
```bash
# ⛔ PHẢI THOÁT môi trường ảo Python TRƯỚC KHI chạy pnpm/node
deactivate     # Thoát .venv nếu đang active

# Kiểm tra đã thoát chưa: dòng terminal không còn tiền tố (.venv)
cd frontend
pnpm install   # hoặc pnpm run dev / pnpm run build
```

> **Lý do**: Nếu đang active `.venv` mà chạy `pnpm`, một số hệ thống sẽ nhầm lẫn PATH, dẫn đến lỗi khó debug. AI phải luôn kiểm tra trạng thái môi trường trước khi chạy lệnh.

---

## 📐 Tiêu chuẩn Chất lượng Mã nguồn (Áp dụng cho mọi Task)

> AI phải đảm bảo các tiêu chuẩn này khi sinh mã trong **tất cả** các task.

### Backend (Python / Flask)
- **Naming**: snake_case cho biến/hàm, PascalCase cho class
- **Docstring**: Mỗi function/class phải có docstring ngắn mô tả chức năng
- **Type hint**: Khuyến khích dùng type hints cho tham số và return value
- **Error handling**: Mọi đoạn gọi DB hoặc external API đều phải có `try/except`, không để lỗi crash server
- **HTTP status code**: Dùng đúng mã (200, 201, 400, 401, 404, 409, 503), không dùng 200 cho lỗi
- **Response format nhất quán**:
  - Thành công: `{"data": ..., "message": "..."}` hoặc `{"coins": [...], "page": 1}`
  - Lỗi: `{"error": "Mô tả lỗi rõ ràng"}`
- **Không hardcode**: Dùng biến môi trường (`.env`) cho SECRET_KEY, DATABASE_URL, API keys
- **Không commit secret**: File `.env` phải có trong `.gitignore`
- **Blueprint tách module**: Mỗi nhóm route là 1 Blueprint riêng biệt

### Frontend (Vue 3 / JavaScript)
- **Naming**: camelCase cho biến/hàm, PascalCase cho component
- **Component tách nhỏ**: Mỗi component chỉ làm 1 việc (Single Responsibility)
- **Props validation**: Mọi prop đều phải khai báo kiểu dữ liệu (`type`, `required`, `default`)
- **Composition API**: Dùng `<script setup>` thay vì Options API
- **Xử lý loading/error**: Mọi API call phải có state `isLoading` và hiển thị lỗi ra UI
- **Không gọi API trực tiếp trong component**: Đặt tất cả API call trong `stores/` hoặc `services/api.js`
- **CSS**: Dùng CSS variables (`:root`) cho màu sắc, không hardcode màu trong component
- **Accessibility cơ bản**: Các button phải có `aria-label`, `<img>` phải có `alt`

---

## Giai đoạn 1: Khởi tạo Dự án & Cấu hình Môi trường

### Task 1.1: Khởi tạo Backend (Flask)

**Công việc:**

- Tạo cấu trúc thư mục `backend/` như sau:
  ```
  backend/
  ├── app/
  │   ├── __init__.py       ← App Factory: khởi tạo Flask, SQLAlchemy, JWT, CORS
  │   ├── models.py
  │   ├── routes/
  │   │   ├── __init__.py
  │   │   ├── auth.py
  │   │   ├── coins.py
  │   │   ├── news.py
  │   │   └── watchlist.py
  │   ├── services/
  │   │   ├── coingecko.py
  │   │   └── crypto_news.py
  │   └── scheduler.py
  ├── tests/
  │   └── __init__.py
  ├── migrations/
  ├── config.py             ← 3 class: DevelopmentConfig, TestingConfig, ProductionConfig
  ├── run.py                ← Entry point
  ├── requirements.txt      ← Dùng phiên bản cụ thể (pin version)
  └── .env                  ← DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY
  ```
- Tạo virtual environment: `python -m venv .venv`
- `config.py`: 3 class kế thừa từ `Config` base — `TestingConfig` dùng SQLite in-memory để test nhanh
- `app/__init__.py`: dùng **App Factory pattern** — hàm `create_app(config_name)` trả về app instance
- Route `GET /` trả `{"message": "Crypto Tracker API", "status": "running"}`
- `requirements.txt` dùng phiên bản cụ thể: `flask==3.0.3`, `flask-sqlalchemy==3.1.1`, v.v.

> **Mẫu `.env`**:
> ```env
> FLASK_ENV=development
> DATABASE_URL=postgresql://postgres:password@localhost:5432/crypto_tracker_dev
> SECRET_KEY=your-super-secret-key-change-this
> JWT_SECRET_KEY=your-jwt-secret-key-change-this
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] App Factory pattern — không có biến `app` global
- [ ] `config.py` đọc giá trị từ `os.environ`, có giá trị mặc định an toàn cho dev
- [ ] `.env` có trong `.gitignore`, không được commit lên git
- [ ] `requirements.txt` dùng phiên bản cụ thể (pin version)

**🧪 Test case:**

```
Lệnh chạy:
  cd backend
  source .venv/bin/activate
  pip install -r requirements.txt
  python run.py
```

| # | Hành động | Input | Kết quả mong đợi |
|---|-----------|-------|-----------------|
| 1 | Cài dependencies | `pip install -r requirements.txt` | Không có lỗi đỏ, terminal in: `Successfully installed flask-3.0.3 ...` |
| 2 | Khởi động server | `python run.py` | Terminal in: `* Running on http://127.0.0.1:5000` |
| 3 | Health check | `GET http://localhost:5000/` | HTTP 200 — `{"message": "Crypto Tracker API", "status": "running"}` |
| 4 | Sai DATABASE_URL | Sửa `.env` thành URL sai | Server log lỗi kết nối rõ ràng, không crash im lặng |

**Kết quả mong đợi:** Flask server khởi động thành công, kết nối được PostgreSQL local.

---

### Task 1.2: Khởi tạo Frontend (Vue 3 + Vite với pnpm)

> ⚠️ **AI lưu ý**: Chạy `deactivate` để thoát `.venv` trước rồi mới thực hiện các bước dưới đây.

**Công việc:**

- Kiểm tra pnpm: `pnpm --version` (yêu cầu >= 8.x). Nếu chưa có: `npm install -g pnpm`
- Khởi tạo: `pnpm create vite@latest frontend -- --template vue`
- Cài dependencies chính: `pnpm add vue-router@4 pinia axios lightweight-charts`
- Cài devDependencies: `pnpm add -D vitest @vue/test-utils jsdom`
- `vite.config.js`: alias `@/` → `./src`, proxy `/api` → `http://localhost:5000`, cấu hình `test.environment: 'jsdom'`
- Tạo cấu trúc `src/`: `views/`, `components/`, `stores/`, `services/`, `router/`, `assets/styles/`
- `src/assets/styles/main.css`: định nghĩa CSS variables cho bảng màu dự án trong `:root {}`
- `router/index.js`: 5 routes dùng lazy import `() => import(...)`, navigation guard kiểm tra auth

> **Tại sao dùng pnpm?** Nhanh hơn npm/yarn, tiết kiệm disk nhờ symlink, `pnpm-lock.yaml` đảm bảo version nhất quán giữa các máy.

> **Mẫu CSS variables trong `:root`**:
> ```css
> :root {
>   --color-black:  #000000;
>   --color-white:  #ffffff;
>   --color-red:    #dd0100;
>   --color-yellow: #fac901;
>   --color-blue:   #225095;
> }
> ```
> Các component chỉ dùng `var(--color-*)`, không hardcode mã hex trực tiếp.

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Chỉ dùng `pnpm`, không dùng `npm`/`yarn` lẫn lộn trong project
- [ ] Alias `@/` hoạt động — kiểm tra bằng cách import thử trong `main.js`
- [ ] Lazy loading routes với `() => import(...)`
- [ ] `pnpm-lock.yaml` được commit vào git (không thêm vào `.gitignore`)

**🧪 Test case:**

```
Lệnh chạy:
  deactivate          ← Thoát .venv trước
  cd frontend
  pnpm install
  pnpm run dev
```

| # | Hành động | Lệnh | Kết quả mong đợi |
|---|-----------|------|-----------------|
| 1 | Cài packages | `pnpm install` | Tạo `node_modules/` và `pnpm-lock.yaml`, terminal in: `Done in Xs` |
| 2 | Khởi động dev | `pnpm run dev` | Terminal in: `VITE v5.x  ready` và `Local: http://localhost:5173/` |
| 3 | Mở browser | `http://localhost:5173` | Trang Vue hiển thị, không có lỗi đỏ trong DevTools Console |
| 4 | Build production | `pnpm run build` | Tạo `dist/`, terminal in: `✓ built in Xs` — không có warning |
| 5 | Chạy test runner | `pnpm run test -- --reporter=verbose` | Vitest khởi động, in: `No test files found` (chưa có test — bình thường) |

**Kết quả mong đợi:** Vue dev server chạy ổn định, routing điều hướng đúng giữa các placeholder views.

---

### Task 1.3: Cấu hình Monorepo & Git

**Công việc:**

- Tạo `.gitignore` ở thư mục gốc bao gồm: `backend/.venv/`, `backend/__pycache__/`, `backend/.env`, `frontend/node_modules/`, `frontend/dist/`, `*.DS_Store`
- `pnpm-lock.yaml` **không** được thêm vào `.gitignore`
- Commit đầu tiên: `git commit -m "chore: initial project structure"`

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] `git status` không hiện file thừa (`.venv`, `node_modules`, `.env`, `dist/`)
- [ ] `pnpm-lock.yaml` được git track

**🧪 Test case:**

| # | Hành động | Lệnh kiểm tra | Kết quả mong đợi |
|---|-----------|---------------|-----------------|
| 1 | Kiểm tra file thừa | `git status` | Chỉ thấy file source code, không thấy `.venv/`, `node_modules/`, `.env` |
| 2 | Kiểm tra lockfile | `git ls-files frontend/pnpm-lock.yaml` | In ra đường dẫn file — xác nhận đã được track |
| 3 | Clone + setup mới | Clone repo vào thư mục khác, làm theo README | Cả backend + frontend khởi động thành công |

**Kết quả mong đợi:** Repo sạch, không commit file nhạy cảm hay file sinh tự động.

---

## Giai đoạn 2: Backend — Database & Models

### Task 2.1: Tạo SQLAlchemy Models

**Công việc:**

- Tạo `app/models.py` với **5 model** theo schema trong README: `User`, `Coin`, `News`, `Watchlist`, `PriceHistory`
- Mỗi model có: docstring mô tả, đầy đủ columns, method `to_dict()` serialize JSON
- `User`: dùng `werkzeug.security` để hash/verify password. `to_dict()` **tuyệt đối không** trả `password_hash`
- `Watchlist`: thêm `UniqueConstraint('user_id', 'coin_id')` ở tầng DB để chặn trùng
- `PriceHistory`: dùng `Numeric(20, 8)` thay vì `Float` để tránh sai số thập phân với tiền tệ
- Dùng `lambda: datetime.now(timezone.utc)` cho default timestamp — tránh `datetime.utcnow` (deprecated Python 3.12)
- `User` → `Watchlist`: relationship dùng `cascade='all, delete-orphan'`

> **Mẫu `to_dict()` của User**: trả `{ "id": 1, "username": "alice", "email": "...", "created_at": "..." }` — không có `password_hash`.

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Mỗi model có docstring
- [ ] `to_dict()` của `User` không chứa `password_hash`
- [ ] Dùng `Numeric` (không phải `Float`) cho cột tiền tệ
- [ ] Timestamp default dùng `lambda: datetime.now(timezone.utc)`
- [ ] Cascade delete đúng (xóa user → xóa watchlist liên quan)

**🧪 Test case:**

```
Lệnh chạy:
  cd backend
  source .venv/bin/activate
  pytest tests/test_models.py -v --tb=long -s
```

| # | Test | Input | Kết quả mong đợi |
|---|------|-------|-----------------|
| 1 | Hash password | `user.set_password('secret123')` | `user.password_hash` khác `'secret123'`, bắt đầu bằng `pbkdf2:sha256:...` |
| 2 | Verify đúng | `user.check_password('secret123')` | Trả `True` |
| 3 | Verify sai | `user.check_password('wrongpass')` | Trả `False` |
| 4 | `to_dict()` User | Gọi `user.to_dict()` | Dict có `id`, `username`, `email`, `created_at` — **không có** key `password_hash` |
| 5 | Trùng watchlist | Thêm 2 lần `(user_id=1, coin_id='bitcoin')` | Raise `IntegrityError` |
| 6 | Cascade delete | Xóa user có watchlist | Watchlist liên quan bị xóa theo, không có orphan record |

```
Kết quả terminal mong đợi:
  ======================== test session starts ========================
  tests/test_models.py::test_user_password_hash PASSED
  tests/test_models.py::test_user_to_dict_no_password PASSED
  tests/test_models.py::test_watchlist_unique_constraint PASSED
  tests/test_models.py::test_cascade_delete PASSED
  ============================== 4 passed in 0.52s ==============================
```

**Kết quả mong đợi:** Tất cả models tạo được, serialize đúng, constraints hoạt động.

---

### Task 2.2: Tạo Database Migration

**Công việc:**

- `flask db init` — tạo `migrations/` (chỉ chạy 1 lần duy nhất)
- `flask db migrate -m "initial schema: users, coins, news, watchlist, price_history"` — tạo migration script
- **Xem lại file migration** tự sinh trước khi apply — kiểm tra đủ 5 bảng và constraints
- `flask db upgrade` — apply vào PostgreSQL
- Commit thư mục `migrations/` vào git

> **Lưu ý**: Sau khi migration đã apply, **không sửa trực tiếp** file migration cũ. Nếu cần thay đổi schema, tạo migration mới.

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Message migration mô tả rõ nội dung thay đổi
- [ ] Thư mục `migrations/` được commit vào git
- [ ] Migration hoạt động 2 chiều: `upgrade` và `downgrade` đều không lỗi

**🧪 Test case:**

```
Lệnh chạy:
  source .venv/bin/activate
  flask db upgrade
  psql -d crypto_tracker_dev -c "\dt"
  psql -d crypto_tracker_dev -c "\d watchlist"
```

| # | Hành động | Lệnh | Kết quả mong đợi |
|---|-----------|------|-----------------|
| 1 | Apply migration | `flask db upgrade` | In: `Running upgrade -> xxxxxxxx, initial schema` — không có lỗi |
| 2 | Kiểm tra bảng | `\dt` trong psql | Thấy đúng 5 bảng: `users`, `coins`, `news`, `watchlist`, `price_history` + `alembic_version` |
| 3 | Kiểm tra constraint | `\d watchlist` | Thấy `UNIQUE (user_id, coin_id)` và 2 foreign keys tới `users` và `coins` |
| 4 | Rollback | `flask db downgrade` | Terminal: `Running downgrade xxxxxxxx -> ...` — xóa tables thành công |
| 5 | Apply lại | `flask db upgrade` | Tạo lại đúng như ban đầu, không lỗi |

```
Kết quả terminal mong đợi (flask db upgrade):
  INFO  [alembic.runtime.migration] Running upgrade  -> a1b2c3d4e5f6,
        initial schema: users, coins, news, watchlist, price_history
```

**Kết quả mong đợi:** Migration hoạt động 2 chiều, schema khớp README.

---

## Giai đoạn 3: Backend — Authentication API

### Task 3.1: API Đăng ký (`POST /api/auth/register`)

**Công việc:**

- Tạo `app/routes/auth.py` — Blueprint `auth_bp` với prefix `/api/auth`
- Tách validation thành hàm helper riêng `validate_register_input(data) -> tuple[bool, str]`, không viết lẫn vào route
  - `username`: 3-50 ký tự
  - `email`: đúng format `x@x.x` dùng regex
  - `password`: tối thiểu 6 ký tự
- Kiểm tra trùng `username`/`email` trong DB trước khi insert
- Bọc DB insert trong `try/except`, gọi `db.session.rollback()` trong `except`
- `.strip()` input trước khi xử lý

> **Mẫu response thành công** (HTTP 201):
> ```json
> { "message": "Đăng ký thành công", "user": { "id": 1, "username": "alice", "email": "alice@mail.com", "created_at": "2024-01-01T00:00:00" } }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Validation tách thành hàm helper độc lập, không lẫn vào route handler
- [ ] `db.session.rollback()` trong mọi `except` block liên quan DB
- [ ] Response không bao giờ chứa `password_hash`
- [ ] `.strip()` input trước khi xử lý

**🧪 Test case:**

```
Lệnh chạy:
  cd backend
  source .venv/bin/activate
  pytest tests/test_auth.py -v --tb=long -s
```

| # | Mô tả | Request body | HTTP | Response body |
|---|-------|-------------|------|---------------|
| 1 | Đăng ký hợp lệ | `{"username":"alice","email":"alice@mail.com","password":"pass123"}` | 201 | `{"message":"Đăng ký thành công","user":{"id":1,"username":"alice",...}}` |
| 2 | Trùng username | `{"username":"alice","email":"new@mail.com","password":"pass123"}` | 409 | `{"error":"Username đã tồn tại"}` |
| 3 | Trùng email | `{"username":"bob","email":"alice@mail.com","password":"pass123"}` | 409 | `{"error":"Email đã tồn tại"}` |
| 4 | Password ngắn | `{"username":"bob","email":"bob@mail.com","password":"123"}` | 400 | `{"error":"Mật khẩu phải ít nhất 6 ký tự"}` |
| 5 | Thiếu field | `{"username":"bob"}` | 400 | `{"error":"Vui lòng điền đầy đủ thông tin"}` |
| 6 | Body không JSON | Text thuần | 400 | `{"error":"Request body phải là JSON"}` |
| 7 | Kiểm tra bảo mật | Response hợp lệ | — | Key `password_hash` **không xuất hiện** trong response |

```
Kết quả terminal mong đợi:
  ======================== test session starts ========================
  tests/test_auth.py::test_register_success PASSED
  tests/test_auth.py::test_register_duplicate_username PASSED
  tests/test_auth.py::test_register_duplicate_email PASSED
  tests/test_auth.py::test_register_short_password PASSED
  tests/test_auth.py::test_register_missing_fields PASSED
  tests/test_auth.py::test_register_no_password_hash_in_response PASSED
  ============================== 6 passed in 0.31s ==============================
```

**Kết quả mong đợi:** Đăng ký hoạt động, validate đúng, hash password an toàn.

---

### Task 3.2: API Đăng nhập (`POST /api/auth/login`)

**Công việc:**

- Implement `POST /api/auth/login`: nhận `{ username, password }`, kiểm tra user tồn tại và password khớp
- Dùng **cùng một message lỗi** cho cả sai username và sai password — tránh để attacker biết username có tồn tại không
- Tạo JWT bằng `create_access_token(identity=str(user.id))` — identity phải là string
- Tạo `tests/test_auth.py` với `@pytest.fixture` cho `app` (dùng `TestingConfig`) và `client`

> **Mẫu response thành công** (HTTP 200):
> ```json
> { "access_token": "eyJhbGciOiJIUzI1NiIs...", "user": { "id": 1, "username": "alice" } }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Cùng error message cho sai username và sai password
- [ ] JWT identity là `str(user.id)` (không phải integer)
- [ ] Test dùng `TestingConfig` với SQLite in-memory — không đụng DB dev

**🧪 Test case:**

```
Lệnh chạy:
  pytest tests/test_auth.py -v --tb=long -s
```

| # | Mô tả | Request body | HTTP | Response body |
|---|-------|-------------|------|---------------|
| 1 | Login đúng | `{"username":"alice","password":"pass123"}` | 200 | `{"access_token":"eyJ...","user":{"id":1,"username":"alice"}}` |
| 2 | Sai username | `{"username":"nobody","password":"pass123"}` | 401 | `{"error":"Sai tên đăng nhập hoặc mật khẩu"}` |
| 3 | Sai password | `{"username":"alice","password":"wrong"}` | 401 | `{"error":"Sai tên đăng nhập hoặc mật khẩu"}` (cùng message) |
| 4 | Thiếu field | `{"username":"alice"}` | 400 | `{"error":"Vui lòng điền username và password"}` |
| 5 | Token hợp lệ | Header `Authorization: Bearer eyJ...` | 200 | API protected trả response thành công |
| 6 | Token sai | Header `Authorization: Bearer invalid` | 401 | `{"msg":"Not enough segments"}` hoặc tương tự |

```
Kết quả terminal mong đợi:
  tests/test_auth.py::test_login_success PASSED
  tests/test_auth.py::test_login_wrong_username PASSED
  tests/test_auth.py::test_login_wrong_password PASSED
  tests/test_auth.py::test_login_missing_fields PASSED
  tests/test_auth.py::test_protected_with_valid_token PASSED
  tests/test_auth.py::test_protected_with_invalid_token PASSED
  ============================== 6 passed in 0.44s ==============================
```

**Kết quả mong đợi:** Login trả JWT, token dùng được cho các API cần auth.

---

### Task 3.3: API Quản lý Tài khoản (`/api/auth/account`)

**Công việc:**

- Thêm 3 endpoint vào `app/routes/auth.py`, tất cả đều có `@jwt_required()`:
  - `PUT /api/auth/account/username` — đổi tên đăng nhập
  - `PUT /api/auth/account/password` — đổi mật khẩu
  - `DELETE /api/auth/account` — xóa tài khoản
- **Yêu cầu xác thực lại**: Cả 3 endpoint đều yêu cầu người dùng cung cấp **`current_password`** trong request body để xác nhận danh tính trước khi thực hiện thay đổi
- Sau khi thực hiện thành công bất kỳ thao tác nào, backend trả về HTTP 200 kèm `{"require_relogin": true}` — frontend phải xử lý bằng cách xóa token và redirect về `/auth`
- **Đổi username**: kiểm tra username mới không trùng với user khác trong DB
- **Đổi password**: yêu cầu `new_password` tối thiểu 6 ký tự, khác `current_password`
- **Xóa tài khoản**: xóa toàn bộ dữ liệu liên quan (watchlist cascade), sau đó xóa user

> **Mẫu request đổi username** (HTTP 200):
> ```json
> Body:   { "new_username": "alice_new", "current_password": "pass123" }
> Response: { "message": "Đổi tên đăng nhập thành công. Vui lòng đăng nhập lại.", "require_relogin": true }
> ```

> **Mẫu request đổi password** (HTTP 200):
> ```json
> Body:   { "current_password": "pass123", "new_password": "newpass456" }
> Response: { "message": "Đổi mật khẩu thành công. Vui lòng đăng nhập lại.", "require_relogin": true }
> ```

> **Mẫu request xóa tài khoản** (HTTP 200):
> ```json
> Body:   { "current_password": "pass123" }
> Response: { "message": "Tài khoản đã được xóa vĩnh viễn." }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] `@jwt_required()` trên cả 3 endpoints
- [ ] Xác minh `current_password` trước khi cho phép bất kỳ thay đổi nào
- [ ] `require_relogin: true` trong response của đổi username và đổi password
- [ ] Đổi username kiểm tra trùng với user khác (không tự so sánh với chính mình)
- [ ] Đổi password không được cho phép `new_password` giống `current_password`
- [ ] Xóa tài khoản dùng cascade — không để lại orphan records
- [ ] `db.session.rollback()` trong mọi `except` liên quan DB

**🧪 Test case:**

```
Lệnh chạy:
  cd backend
  source .venv/bin/activate
  pytest tests/test_account.py -v --tb=long -s
```

| # | Endpoint | Request body | HTTP | Response body |
|---|----------|-------------|------|---------------|
| 1 | `PUT /username` | Không có token | 401 | `{"msg":"Missing Authorization Header"}` |
| 2 | `PUT /username` | `{"new_username":"alice2","current_password":"pass123"}` + token | 200 | `{"message":"Đổi tên đăng nhập thành công...","require_relogin":true}` |
| 3 | `PUT /username` | `{"new_username":"bob","current_password":"pass123"}` (bob đã tồn tại) | 409 | `{"error":"Username đã tồn tại"}` |
| 4 | `PUT /username` | `{"new_username":"alice2","current_password":"wrongpass"}` | 401 | `{"error":"Mật khẩu hiện tại không đúng"}` |
| 5 | `PUT /username` | `{"new_username":""}` | 400 | `{"error":"Username mới không được để trống"}` |
| 6 | `PUT /password` | `{"current_password":"pass123","new_password":"newpass456"}` + token | 200 | `{"message":"Đổi mật khẩu thành công...","require_relogin":true}` |
| 7 | `PUT /password` | `{"current_password":"pass123","new_password":"pass123"}` | 400 | `{"error":"Mật khẩu mới không được giống mật khẩu hiện tại"}` |
| 8 | `PUT /password` | `{"current_password":"pass123","new_password":"123"}` | 400 | `{"error":"Mật khẩu mới phải ít nhất 6 ký tự"}` |
| 9 | `PUT /password` | `{"current_password":"wrongpass","new_password":"newpass456"}` | 401 | `{"error":"Mật khẩu hiện tại không đúng"}` |
| 10 | `DELETE /account` | `{"current_password":"pass123"}` + token | 200 | `{"message":"Tài khoản đã được xóa vĩnh viễn."}` |
| 11 | `DELETE /account` | `{"current_password":"wrongpass"}` | 401 | `{"error":"Mật khẩu hiện tại không đúng"}` |
| 12 | Sau DELETE | Dùng token cũ gọi bất kỳ API | 401 | Token không còn hợp lệ (user không còn tồn tại) |

```
Kết quả terminal mong đợi:
  ======================== test session starts ========================
  tests/test_account.py::test_change_username_no_auth PASSED
  tests/test_account.py::test_change_username_success PASSED
  tests/test_account.py::test_change_username_duplicate PASSED
  tests/test_account.py::test_change_username_wrong_password PASSED
  tests/test_account.py::test_change_username_empty PASSED
  tests/test_account.py::test_change_password_success PASSED
  tests/test_account.py::test_change_password_same_as_current PASSED
  tests/test_account.py::test_change_password_too_short PASSED
  tests/test_account.py::test_change_password_wrong_current PASSED
  tests/test_account.py::test_delete_account_success PASSED
  tests/test_account.py::test_delete_account_wrong_password PASSED
  tests/test_account.py::test_token_invalid_after_delete PASSED
  ============================== 12 passed in 0.61s ==============================
```

**Kết quả mong đợi:** Cả 3 thao tác hoạt động đúng, xác thực mật khẩu hiện tại trước khi cho phép thay đổi, backend ra hiệu yêu cầu đăng nhập lại.

---

## Giai đoạn 4: Backend — Coins & News API

### Task 4.1: CoinGecko Service

**Công việc:**

- Tạo `app/services/coingecko.py` với hàm helper dùng chung `_get_with_retry(url, params, max_retries=3)`
- Retry **exponential backoff**: lần 0 không chờ, lần 1 chờ 1s, lần 2 chờ 2s, lần 3 chờ 4s (`wait = 2 ** attempt`)
- Xử lý: `Timeout`, `429 Too Many Requests`, `5xx Server Error`
- Trả `None` khi hết retry — không raise exception ra ngoài
- 3 hàm public: `fetch_top_coins(page, per_page)`, `fetch_coin_detail(coin_id)`, `fetch_coin_history(coin_id, days=7)`

> **Mẫu xử lý 429**:
> ```python
> if response.status_code == 429:
>     wait_time = 2 ** attempt
>     logger.warning(f'Rate limit. Retry sau {wait_time}s...')
>     time.sleep(wait_time)
>     continue
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Hàm `_get_with_retry` dùng chung, không copy-paste code retry ở nhiều nơi
- [ ] Log rõ ràng mỗi lần retry và lỗi cuối cùng
- [ ] Trả `None` khi thất bại, không raise exception
- [ ] Timeout mặc định 10 giây

**🧪 Test case:**

```
Lệnh chạy:
  pytest tests/test_services.py -v --tb=long -s
```

| # | Mô tả | Điều kiện | Kết quả mong đợi |
|---|-------|-----------|-----------------|
| 1 | Fetch coins | `fetch_top_coins(1, 25)` thật | Trả list 25 phần tử, mỗi phần tử có `id`, `symbol`, `current_price`, `image` |
| 2 | Fetch detail | `fetch_coin_detail("bitcoin")` thật | Trả dict có `market_data.current_price.usd` là số dương |
| 3 | Fetch history | `fetch_coin_history("bitcoin", 7)` thật | Trả dict có `prices` là list `[[timestamp_ms, price], ...]`, đủ ~168 điểm (7 ngày × 24h) |
| 4 | Retry khi 429 | Mock `requests.get` trả 429 liên tục | Thử 3 lần, mỗi lần log warning, cuối cùng trả `None` |
| 5 | Timeout | Mock `requests.get` raise `Timeout` | Trả `None`, log error — server không crash |

```
Kết quả terminal mong đợi:
  tests/test_services.py::test_fetch_top_coins_structure PASSED
  tests/test_services.py::test_fetch_coin_detail_structure PASSED
  tests/test_services.py::test_retry_on_429 PASSED
  tests/test_services.py::test_timeout_returns_none PASSED
  ============================== 4 passed in 1.23s ==============================
```

**Kết quả mong đợi:** Service fetch dữ liệu ổn định, retry đúng logic, không crash khi lỗi.

---

### Task 4.2: Coins Routes

**Công việc:**

- Tạo `app/routes/coins.py` — Blueprint `coins_bp`
- **Chiến lược cache**: Luôn query DB trước, chỉ gọi CoinGecko khi DB trống — tránh rate limit
- **Quan trọng**: Đặt route `GET /search` **trước** route `GET /<coin_id>` trong code để Flask không nhầm "search" là coin_id
- Tìm kiếm dùng `ilike` (case-insensitive) trong cả `name` và `symbol`
- Upsert coins: cập nhật nếu đã có, thêm mới nếu chưa có
- Trả HTTP 503 (không phải 500) khi external API không phản hồi

> **Mẫu phân trang response**:
> ```json
> { "coins": [...], "page": 1, "per_page": 25, "total": 100, "total_pages": 4 }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Route `/search` đặt trước `/<coin_id>` trong file
- [ ] DB-first: query DB trước, fallback CoinGecko khi DB trống
- [ ] HTTP 503 khi external API lỗi
- [ ] `ilike` cho tìm kiếm case-insensitive

**🧪 Test case:**

```
Lệnh chạy:
  pytest tests/test_coins.py -v --tb=long -s
```

| # | Endpoint | Input | HTTP | Response |
|---|----------|-------|------|----------|
| 1 | `GET /api/coins/?page=1` | — | 200 | `{"coins":[...25 items...],"page":1,"per_page":25,"total":100,"total_pages":4}` |
| 2 | `GET /api/coins/?page=2` | — | 200 | `{"coins":[...25 items...],"page":2}` |
| 3 | `GET /api/coins/bitcoin` | — | 200 | `{"coin":{"id":"bitcoin","name":"Bitcoin","symbol":"BTC",...}}` |
| 4 | `GET /api/coins/invalid-xyz` | — | 404 | `{"error":"Không tìm thấy coin: invalid-xyz"}` |
| 5 | `GET /api/coins/bitcoin/history` | — | 200 | `{"prices":[[1700000000000,42000.5],[1700086400000,42100.2],...]}` |
| 6 | `GET /api/coins/search?q=bit` | — | 200 | `{"coins":[{"id":"bitcoin","name":"Bitcoin"},{"id":"bitcoin-cash",...}]}` |
| 7 | `GET /api/coins/search?q=ETH` | — | 200 | Tìm được ethereum (case-insensitive) |
| 8 | `GET /api/coins/search?q=` | — | 400 | `{"error":"Tham số q không được để trống"}` |

```
Kết quả terminal mong đợi:
  tests/test_coins.py::test_get_coins_page1 PASSED
  tests/test_coins.py::test_get_coins_page2 PASSED
  tests/test_coins.py::test_get_coin_detail PASSED
  tests/test_coins.py::test_get_coin_not_found PASSED
  tests/test_coins.py::test_get_coin_history PASSED
  tests/test_coins.py::test_search_coins PASSED
  tests/test_coins.py::test_search_case_insensitive PASSED
  tests/test_coins.py::test_search_empty_query PASSED
  ============================== 8 passed in 0.67s ==============================
```

**Kết quả mong đợi:** Tất cả endpoint coins hoạt động, phân trang đúng 25 items/trang.

---

### Task 4.3: News Service & Routes

**Công việc:**

- Tạo `app/services/crypto_news.py` với `fetch_and_save_news() -> int`:
  - Gọi `https://cryptocurrency.cv/api/news`, parse response
  - Bỏ qua URL đã có trong DB
  - `db.session.commit()` **một lần** sau vòng lặp — không commit từng item
  - Trả số tin mới được lưu
- Tách hàm `_parse_date(date_str)` để xử lý nhiều format date, có fallback về `datetime.now()`
- Tạo `app/routes/news.py` — `GET /api/news/` với phân trang và `?q=` search

> **Mẫu response** (HTTP 200):
> ```json
> { "news": [{"id":1,"title":"Bitcoin hits...","url":"https://...","source":"CoinDesk","published_at":"2024-01-01T..."}], "page":1,"total":50,"total_pages":3 }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] `commit()` một lần sau vòng lặp
- [ ] `_parse_date()` tách riêng, có fallback
- [ ] Xử lý linh hoạt field `source` (string hoặc dict)

**🧪 Test case:**

```
Lệnh chạy:
  pytest tests/test_news.py -v --tb=long -s
```

| # | Mô tả | Điều kiện | Kết quả mong đợi |
|---|-------|-----------|-----------------|
| 1 | Fetch lần 1 | Mock API trả 5 bài mới | Trả `5`, DB có 5 bản ghi news |
| 2 | Fetch lần 2 | Mock API trả cùng 5 bài | Trả `0`, DB vẫn chỉ có 5 bản ghi |
| 3 | GET danh sách | DB có 10 tin | `{"news":[...10 items...],"page":1,"total":10,"total_pages":1}` |
| 4 | GET tìm kiếm | `?q=bitcoin` | Chỉ trả tin có "bitcoin" trong title |
| 5 | GET tìm không có | `?q=xyznotexist` | `{"news":[],"total":0,"total_pages":0}` |

```
Kết quả terminal mong đợi:
  tests/test_news.py::test_fetch_saves_new_articles PASSED
  tests/test_news.py::test_fetch_no_duplicate PASSED
  tests/test_news.py::test_get_news_list PASSED
  tests/test_news.py::test_search_news PASSED
  tests/test_news.py::test_search_no_result PASSED
  ============================== 5 passed in 0.38s ==============================
```

**Kết quả mong đợi:** Fetch đúng, không tạo bản ghi trùng, search hoạt động.

---

### Task 4.4: Watchlist Routes

**Công việc:**

- Tạo `app/routes/watchlist.py` — Blueprint `watchlist_bp`
- Tất cả 3 endpoints có decorator `@jwt_required()`
- `POST`: Kiểm tra coin tồn tại trong bảng `coins` trước. Bắt `IntegrityError` cho trường hợp trùng
- `DELETE`: Lọc theo cả `user_id` VÀ `coin_id` — tránh user xóa watchlist của người khác
- `GET`: Join với bảng `coins` để trả đầy đủ thông tin coin

> **Mẫu response GET** (HTTP 200):
> ```json
> { "watchlist": [{ "id":1, "coin_id":"bitcoin", "added_at":"...", "coin":{"id":"bitcoin","name":"Bitcoin","symbol":"BTC",...} }] }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] `@jwt_required()` trên cả 3 endpoints
- [ ] Kiểm tra coin tồn tại trước khi thêm
- [ ] DELETE filter cả `user_id` và `coin_id`
- [ ] Bắt `IntegrityError` thay vì chỉ kiểm tra trước insert

**🧪 Test case:**

```
Lệnh chạy:
  pytest tests/test_watchlist.py -v --tb=long -s
```

| # | Endpoint | Điều kiện | HTTP | Response |
|---|----------|-----------|------|----------|
| 1 | `GET /api/watchlist/` | Không có token | 401 | `{"msg":"Missing Authorization Header"}` |
| 2 | `POST /api/watchlist/` | `{"coin_id":"bitcoin"}` + token | 201 | `{"message":"Đã thêm vào watchlist","item":{"coin_id":"bitcoin",...}}` |
| 3 | `POST /api/watchlist/` | Thêm "bitcoin" lần 2 + token | 409 | `{"error":"Coin đã có trong watchlist"}` |
| 4 | `POST /api/watchlist/` | `{"coin_id":"not-exist"}` + token | 404 | `{"error":"Coin not-exist không tồn tại trong hệ thống"}` |
| 5 | `GET /api/watchlist/` | Sau khi thêm bitcoin + token | 200 | `{"watchlist":[{"coin_id":"bitcoin","coin":{"name":"Bitcoin",...}}]}` |
| 6 | `DELETE /api/watchlist/bitcoin` | Token hợp lệ | 200 | `{"message":"Đã xóa bitcoin khỏi watchlist"}` |
| 7 | `DELETE /api/watchlist/bitcoin` | Xóa lần 2 | 404 | `{"error":"Coin không có trong watchlist của bạn"}` |

```
Kết quả terminal mong đợi:
  tests/test_watchlist.py::test_get_watchlist_no_auth PASSED
  tests/test_watchlist.py::test_add_coin PASSED
  tests/test_watchlist.py::test_add_duplicate_coin PASSED
  tests/test_watchlist.py::test_add_nonexistent_coin PASSED
  tests/test_watchlist.py::test_get_watchlist PASSED
  tests/test_watchlist.py::test_delete_coin PASSED
  tests/test_watchlist.py::test_delete_nonexistent PASSED
  ============================== 7 passed in 0.55s ==============================
```

**Kết quả mong đợi:** CRUD watchlist hoạt động đúng, auth protection trên tất cả endpoints.

---

## Giai đoạn 5: Backend — APScheduler & Tác vụ ngầm

### Task 5.1: Cấu hình APScheduler

**Công việc:**

- Tạo `app/scheduler.py` với hàm `init_scheduler(app)`:
  - Job `update_coins`: upsert `coins` + thêm snapshot `price_history` — mỗi 30 phút
  - Job `update_news`: lưu tin mới — mỗi 15 phút
- Tích hợp vào App Factory: chỉ gọi khi `config_name != 'testing'`
- Dùng `replace_existing=True` khi đăng ký job — tránh trùng khi hot-reload
- Đăng ký `atexit.register(lambda: scheduler.shutdown(wait=False))` để dừng sạch
- Mỗi job bọc trong `with app.app_context()` và `try/except`

> **Mẫu logging mỗi lần job chạy**:
> - Coins: `[Scheduler] Đã cập nhật 100 coins, thêm 100 price records`
> - News: `[Scheduler] Đã lưu 5 tin mới`

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] `replace_existing=True` tránh job trùng khi reload
- [ ] `atexit.register` để scheduler dừng sạch
- [ ] Không khởi chạy scheduler trong môi trường `testing`
- [ ] Mỗi job bọc `app_context()` và `try/except`

**🧪 Test case:**

| # | Mô tả | Điều kiện | Kết quả mong đợi |
|---|-------|-----------|-----------------|
| 1 | Khởi động | Start server | Log: `[Scheduler] Đã khởi động` |
| 2 | Job coins | Trigger thủ công hoặc đợi 30 phút | Log: `[Scheduler] Đã cập nhật 100 coins, thêm 100 price records` |
| 3 | Job news | Trigger thủ công hoặc đợi 15 phút | Log: `[Scheduler] Đã lưu X tin mới` |
| 4 | API lỗi | Mock CoinGecko trả exception | Log error, server **không** crash |
| 5 | Hot-reload | Lưu file → Flask reload | Chỉ 1 scheduler instance, không chạy 2 lần đồng thời |

**Kết quả mong đợi:** Dữ liệu tự cập nhật định kỳ, server ổn định khi external API lỗi.

---

## Giai đoạn 6: Frontend — Xây dựng Giao diện

> ⚠️ **AI lưu ý**: Trước khi chạy bất kỳ lệnh `pnpm` nào trong Giai đoạn 6:
> ```bash
> deactivate    # Thoát .venv nếu đang active
> cd frontend
> ```

### Task 6.1: Layout & Navigation chung

**Công việc:**

- Tạo `src/services/api.js` — axios instance duy nhất:
  - Request interceptor: tự gắn `Authorization: Bearer <token>` vào header
  - Response interceptor: nhận 401 → xóa token localStorage → redirect `/auth`
- Tạo `src/stores/auth.js` (Pinia, Composition API):
  - State `token`, `user` — khởi tạo từ `localStorage` để persist sau reload
  - Actions: `login()`, `register()`, `logout()`
  - Getter `isAuthenticated`: `computed(() => !!token.value)`
- Tạo `App.vue` với Navbar responsive (hamburger ≤768px), ẩn/hiện link theo `isAuthenticated`

> **Mẫu axios instance**:
> ```js
> const api = axios.create({ baseURL: '/api', timeout: 10000 })
> // Tất cả component chỉ import { api } từ file này
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Tất cả API call đi qua `api.js` — không `import axios` trực tiếp trong component
- [ ] Auth store persist vào `localStorage`
- [ ] Pinia dùng Composition API (`defineStore` với setup function)
- [ ] Navigation guard redirect về `/auth` cho route `meta: { requiresAuth: true }`

**🧪 Test case:**

```
Lệnh chạy thủ công:
  deactivate && cd frontend && pnpm run dev
```

| # | Hành động | Kết quả mong đợi |
|---|-----------|-----------------|
| 1 | Desktop — mở app | Navbar hiện đủ: Logo, Home, News, nút Login |
| 2 | Mobile (≤768px) | Navbar thu gọn, hiện icon hamburger ☰ |
| 3 | Click hamburger | Menu dropdown mở/đóng mượt mà |
| 4 | Chưa login → `/watchlist` | Redirect tự động về `/auth` |
| 5 | Sau login → reload page | Vẫn giữ trạng thái đăng nhập |
| 6 | Logout | Token xóa khỏi localStorage, Navbar về trạng thái ban đầu |

---

### Task 6.2: AuthView (Login/Register)

**Công việc:**

- `views/AuthView.vue`: 2 form trong 1 view, toggle bằng `isLoginMode`
- Validation client-side trước khi gọi API (không để request thừa)
- State: `isLoading` (disable button + spinner), `errorMsg` (hiện lỗi từ API)
- Mọi async call dùng `try/catch/finally` — `finally` đảm bảo reset `isLoading = false`

> **Mẫu xử lý lỗi từ API**:
> ```js
> } catch (err) {
>   errorMsg.value = err.response?.data?.error || 'Đã có lỗi xảy ra'
> } finally {
>   isLoading.value = false
> }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] `finally` block luôn reset `isLoading = false`
- [ ] Lỗi API hiển thị ra UI — không chỉ `console.log`
- [ ] Button disabled khi `isLoading === true`
- [ ] Input có `autocomplete` attribute (`username`, `current-password`, `email`)

**🧪 Test case:**

| # | Hành động | Input | Kết quả mong đợi |
|---|-----------|-------|-----------------|
| 1 | Mở `/auth` | — | Form Login hiển thị mặc định |
| 2 | Click "Đăng ký" | — | Chuyển sang form Register có animation |
| 3 | Submit form rỗng | Không nhập gì | Hiện lỗi validation ngay, **không** gọi API |
| 4 | Password không khớp | `pass: "abc123"`, `confirm: "abc456"` | Hiện: "Mật khẩu xác nhận không khớp" |
| 5 | Login đúng | `alice / pass123` | Redirect Home, Navbar hiện "alice" + Logout |
| 6 | Login sai | `alice / wrong` | Hiện error: "Sai tên đăng nhập hoặc mật khẩu" |
| 7 | Click nhiều lần khi loading | Nhấp liên tục | Button disabled, chỉ gửi 1 request |

---

### Task 6.3: AccountSettingsView (Cài đặt tài khoản)

**Công việc:**

- Thêm route `/settings` vào `router/index.js` với `meta: { requiresAuth: true }`
- Tạo `views/AccountSettingsView.vue` với 3 section riêng biệt trong cùng 1 trang:
  - **Đổi tên đăng nhập**: input `new_username` + input `current_password` + nút xác nhận
  - **Đổi mật khẩu**: input `current_password` + input `new_password` + input `confirm_password` + nút xác nhận
  - **Xóa tài khoản**: vùng nguy hiểm (danger zone) với màu đỏ, input `current_password` + nút "Xóa tài khoản vĩnh viễn"
- Mỗi section có state `isLoading` và `errorMsg` riêng — lỗi của section nào hiện ở section đó
- **Xử lý `require_relogin`**: khi nhận `require_relogin: true` từ response, gọi `authStore.logout()` rồi redirect `/auth` kèm query param `?reason=relogin` để AuthView hiển thị thông báo phù hợp
- AuthView đọc query `?reason=relogin` và hiện banner "Thông tin đăng nhập đã thay đổi. Vui lòng đăng nhập lại."
- Thêm link "Cài đặt tài khoản" vào Navbar (chỉ hiện khi đã đăng nhập)

> **Mẫu xử lý require_relogin trong mỗi action**:
> ```js
> const { data } = await api.put('/auth/account/username', payload)
> if (data.require_relogin) {
>   authStore.logout()
>   router.push({ name: 'Auth', query: { reason: 'relogin' } })
> }
> ```

> **Mẫu danger zone**: Section xóa tài khoản dùng `border: 2px solid var(--color-red)`, background nhạt hơn để người dùng nhận biết đây là hành động không thể hoàn tác.

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Mỗi section có state `isLoading` và `errorMsg` độc lập
- [ ] `finally` block reset `isLoading = false` sau mỗi request
- [ ] Redirect về `/auth?reason=relogin` sau khi thao tác thành công
- [ ] AuthView đọc query `reason` và hiện banner thông báo
- [ ] Danger zone phân biệt rõ bằng màu sắc, có text cảnh báo "Hành động không thể hoàn tác"
- [ ] Validation client-side: `confirm_password` phải khớp `new_password` trước khi gửi request

**🧪 Test case:**

```
Lệnh chạy thủ công:
  deactivate && cd frontend && pnpm run dev
```

| # | Hành động | Input | Kết quả mong đợi |
|---|-----------|-------|-----------------|
| 1 | Chưa login → `/settings` | — | Redirect về `/auth` (navigation guard) |
| 2 | Mở `/settings` sau khi login | — | Trang hiện 3 section rõ ràng: Đổi username, Đổi password, Xóa tài khoản |
| 3 | Đổi username — sai mật khẩu | `new_username: "alice2"`, `current_password: "wrong"` | Section đổi username hiện lỗi: "Mật khẩu hiện tại không đúng" |
| 4 | Đổi username — thành công | `new_username: "alice2"`, `current_password: "pass123"` | Toast "Đổi tên thành công", tự động logout, redirect `/auth?reason=relogin` |
| 5 | AuthView nhận `reason=relogin` | — | Banner "Thông tin đăng nhập đã thay đổi. Vui lòng đăng nhập lại." |
| 6 | Đổi password — không khớp confirm | `new: "abc123"`, `confirm: "abc456"` | Lỗi client-side: "Mật khẩu xác nhận không khớp", không gửi request |
| 7 | Đổi password — thành công | `current: "pass123"`, `new: "newpass456"` | Logout tự động, redirect `/auth?reason=relogin` |
| 8 | Xóa tài khoản — sai mật khẩu | `current_password: "wrong"` | Section danger zone hiện lỗi: "Mật khẩu hiện tại không đúng" |
| 9 | Xóa tài khoản — thành công | `current_password: "pass123"` | Toast "Tài khoản đã được xóa", redirect `/auth`, không thể login lại với account cũ |
| 10 | Đang thực hiện 1 thao tác | Click nút nhiều lần | Button disabled, chỉ gửi 1 request |

---

### Task 6.4: HomeView (CoinTable)

**Công việc:**

- Tạo `src/stores/coinStore.js`: state `coins`, `totalPages`, `isLoading`, `error` — action `fetchCoins(page)`
- Tạo `components/CoinTable.vue`:
  - Props: `coins` (Array, required), `mode` (String, default `'default'`)
  - Cột 24h%: class động — xanh lá khi dương, đỏ khi âm + icon ▲/▼
  - Nút ➕ khi `mode==='default'` + `isAuthenticated`; nút 🗑️ khi `mode==='watchlist'`
- Tạo `views/HomeView.vue`: search bar debounce 300ms, skeleton loading, pagination

> **Mẫu debounce đơn giản**:
> ```js
> let timer = null
> watch(searchQuery, (val) => {
>   clearTimeout(timer)
>   timer = setTimeout(() => fetchCoins(1, val), 300)
> })
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Skeleton loading khi `isLoading === true`
- [ ] Error state hiển thị ra UI khi API lỗi
- [ ] Debounce 300ms trên search
- [ ] Props validation đầy đủ trong `CoinTable.vue`

**🧪 Test case:**

| # | Hành động | Kết quả mong đợi |
|---|-----------|-----------------|
| 1 | Load trang Home | Skeleton hiện trước → 25 coins hiển thị sau |
| 2 | Giá tăng 24h | Cột % màu xanh lá + icon ▲ |
| 3 | Giá giảm 24h | Cột % màu đỏ + icon ▼ |
| 4 | Click "Next" hoặc page 2 | Load 25 coins tiếp theo |
| 5 | Search "eth" | Sau 300ms debounce, filter ra coin có "eth" |
| 6 | Xóa text search | Quay lại danh sách đầy đủ |
| 7 | Click row bitcoin | Chuyển đến `/coin/bitcoin` |
| 8 | Đã login → Click ➕ bitcoin | Toast "Đã thêm Bitcoin", icon đổi thành ✓ |
| 9 | Mobile | Bảng scroll ngang, cột Tên + Giá luôn hiển thị |

---

### Task 6.5: CoinDetailView (Biểu đồ giá)

**Công việc:**

> ⚠️ `deactivate` trước: `pnpm add lightweight-charts`

- Tạo `components/PriceChart.vue` dùng TradingView Lightweight Charts:
  - `onMounted`: khởi tạo chart và series
  - `onUnmounted`: gọi `chart.remove()` — **bắt buộc** để tránh memory leak
  - `watch(prices)`: cập nhật series khi dữ liệu thay đổi
  - Convert timestamp: API trả milliseconds → chart cần seconds (`Math.floor(ts / 1000)`)
- Tạo `views/CoinDetailView.vue`: header coin info, `PriceChart`, stats (Market Cap, Volume, ATH, ATL), nút "So sánh"

> **Mẫu convert timestamp**:
> ```js
> const data = prices.map(([ts, value]) => ({ time: Math.floor(ts / 1000), value }))
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] `onUnmounted(() => chart?.remove())` — bắt buộc
- [ ] `watch` prices để re-render khi data thay đổi
- [ ] Hiện trang 404 khi coin không tồn tại
- [ ] Biểu đồ responsive theo width màn hình

**🧪 Test case:**

| # | Hành động | Kết quả mong đợi |
|---|-----------|-----------------|
| 1 | Mở `/coin/bitcoin` | Biểu đồ 7 ngày render, header hiện giá Bitcoin |
| 2 | Hover biểu đồ | Tooltip hiện giá + ngày giờ tại điểm hover |
| 3 | Resize cửa sổ | Biểu đồ co giãn theo width |
| 4 | Mở `/coin/xyz-not-exist` | Trang 404 với nút "Về trang chủ" |
| 5 | Navigate sang coin khác | Biểu đồ cũ cleanup, không rò rỉ bộ nhớ |

---

### Task 6.6: CompareChart (So sánh 2 coin)

**Công việc:**

- Tạo `components/CompareChart.vue`:
  - Input search với debounce, gọi `GET /api/coins/search?q=`, hiện dropdown kết quả
  - 2 `LineSeries`: coin 1 màu `#225095` (xanh), coin 2 màu `#fac901` (vàng)
  - Toggle kiểu: Line / Area
  - Checkbox Normalize: `% thay đổi = ((price - basePrice) / basePrice) * 100`

> **Mẫu normalize**:
> ```js
> function normalize(prices) {
>   const base = prices[0][1]
>   return prices.map(([ts, p]) => ({ time: Math.floor(ts/1000), value: ((p-base)/base)*100 }))
> }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Debounce search 300ms
- [ ] Xử lý khi coin 2 chưa chọn (chỉ hiện 1 line)
- [ ] Legend rõ tên + màu từng coin
- [ ] Cleanup cả 2 series khi unmount

**🧪 Test case:**

| # | Hành động | Kết quả mong đợi |
|---|-----------|-----------------|
| 1 | Click "So sánh" | Input search hiện ra |
| 2 | Nhập "eth" | Dropdown hiện coin chứa "eth" sau 300ms |
| 3 | Chọn Ethereum | Biểu đồ hiện 2 lines: BTC xanh + ETH vàng, có legend |
| 4 | Toggle "Area" | Cả 2 series chuyển sang kiểu area |
| 5 | Bật Normalize | Trục Y đổi sang %, cả 2 coin bắt đầu từ 0% |
| 6 | Hover | Tooltip hiện giá/% của cả 2 coin |

---

### Task 6.7: NewsView

**Công việc:**

- Tạo `components/NewsCard.vue`:
  - Props: `article` (Object, required)
  - Thẻ `<a target="_blank" rel="noopener noreferrer">` — bắt buộc có `rel` để bảo mật
  - Format ngày theo locale Việt Nam
- Tạo `views/NewsView.vue`: CSS Grid `auto-fill` responsive, search debounce 300ms, empty state

> **Mẫu CSS Grid responsive**:
> ```css
> .news-grid {
>   display: grid;
>   grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
>   gap: 1rem;
> }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] `rel="noopener noreferrer"` trên mọi link `target="_blank"`
- [ ] Empty state khi list rỗng
- [ ] CSS Grid `auto-fill` tự responsive, không cần media query

**🧪 Test case:**

| # | Hành động | Kết quả mong đợi |
|---|-----------|-----------------|
| 1 | Mở `/news` | Skeleton → Grid tin tức hiển thị |
| 2 | Xem card | Hiện title, source, ngày dạng "1 thg 1, 2024" (vi-VN) |
| 3 | Click card | Mở URL trong tab mới |
| 4 | Search "bitcoin" | Sau 300ms chỉ hiện tin có "bitcoin" |
| 5 | Search không có kết quả | Empty state "Không tìm thấy tin tức phù hợp" |
| 6 | Desktop → Mobile | Grid tự co từ 3 cột → 1 cột |

---

### Task 6.8: WatchlistView

**Công việc:**

- Tạo `src/stores/watchlist.js`:
  - `addCoin`: gọi POST → push coin vào `coins.value` ngay (optimistic update)
  - `removeCoin`: gọi DELETE → `filter` khỏi `coins.value` ngay — không fetch lại
  - Getter `hasCoin(coinId)`: trả boolean — dùng trong CoinTable để đổi icon ➕ → ✓
- Tạo `views/WatchlistView.vue`: reuse `<CoinTable mode="watchlist">`, empty state có nút "Khám phá ngay"

> **Mẫu optimistic update**:
> ```js
> async function removeCoin(coinId) {
>   await api.delete(`/watchlist/${coinId}`)
>   coins.value = coins.value.filter(item => item.coin_id !== coinId) // cập nhật ngay
> }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Getter `hasCoin()` để CoinTable biết trạng thái từng coin
- [ ] Optimistic update: cập nhật local state ngay sau action thành công
- [ ] Navigation guard đã xử lý redirect, không cần check trong component

**🧪 Test case:**

| # | Hành động | Kết quả mong đợi |
|---|-----------|-----------------|
| 1 | Chưa login → `/watchlist` | Redirect tự động về `/auth` |
| 2 | Login → Watchlist trống | Empty state + nút "Khám phá ngay" |
| 3 | Từ Home thêm Bitcoin | Icon ➕ đổi ✓ ngay, toast "Đã thêm Bitcoin" |
| 4 | Vào Watchlist | Bitcoin xuất hiện trong danh sách |
| 5 | Click 🗑️ | Coin biến mất ngay khỏi danh sách, toast "Đã xóa" |
| 6 | Click row | Điều hướng đến `/coin/bitcoin` |

---

## Giai đoạn 7: Polish, Testing & Deployment

### Task 7.1: UI Polish & Animations

**Công việc:**

- **Skeleton loading**: `SkeletonRow.vue` (6 ô cho CoinTable) và `SkeletonCard.vue` (cho news) — dùng CSS animation `pulse`
- **Toast notification**: `ToastNotification.vue` — tự biến mất sau 3s, hiện góc dưới phải, không block interaction
- **Page transition**: `<Transition>` trong `App.vue` bọc `<RouterView>` — animation fade/slide
- **Error pages**: `NotFoundView.vue` (404) với nút "Về trang chủ"
- **Document title**: thay đổi `document.title` theo `router.meta.title` mỗi route

> **Mẫu CSS skeleton animation**:
> ```css
> @keyframes pulse {
>   0%   { background-position: 200% 0; }
>   100% { background-position: -200% 0; }
> }
> .skeleton {
>   background: linear-gradient(90deg, var(--color-surface) 25%, var(--color-border) 50%, var(--color-surface) 75%);
>   background-size: 200% 100%;
>   animation: pulse 1.5s ease-in-out infinite;
> }
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Skeleton đúng số cột của CoinTable (6 cột)
- [ ] Toast `position: fixed`, không overlay nội dung chính
- [ ] Page transition không gây layout shift

**🧪 Test case:**

| # | Hành động | Kết quả mong đợi |
|---|-----------|-----------------|
| 1 | Load trang (network chậm) | Skeleton hiện thay vì blank trắng |
| 2 | Thêm coin vào watchlist | Toast xanh "Đã thêm Bitcoin vào watchlist", tự mất sau 3s |
| 3 | Xóa coin | Toast đỏ "Đã xóa Bitcoin" |
| 4 | Chuyển trang | Fade animation mượt, không giật |
| 5 | Vào URL không tồn tại `/xyz` | Trang 404, tab title "404 — Không tìm thấy" |
| 6 | Vào `/coin/bitcoin` | Tab title "Bitcoin — Crypto Tracker" |

---

### Task 7.2: Unit Test

**Công việc:**

- **Backend (pytest)**: 5 file test
  - `tests/conftest.py` — fixtures `app`, `client`, `auth_headers`
  - `tests/test_auth.py` — register, login, validation, token
  - `tests/test_account.py` — đổi username, đổi password, xóa tài khoản, xác thực mật khẩu hiện tại
  - `tests/test_coins.py` — list, detail, search, history, 404
  - `tests/test_watchlist.py` — CRUD, auth required, duplicate
- **Frontend (vitest)**: 3 file test
  - `tests/stores/auth.test.js` — login action, logout, `isAuthenticated`
  - `tests/components/CoinTable.test.js` — render props, hiện/ẩn nút theo mode
  - `tests/views/AccountSettings.test.js` — validation client-side, xử lý `require_relogin`

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Backend test dùng `TestingConfig` (SQLite in-memory)
- [ ] Mỗi test độc lập, không phụ thuộc thứ tự
- [ ] Coverage mục tiêu ≥ 70% cho backend

**🧪 Test case:**

```
Lệnh chạy Backend (đầy đủ output, không ẩn tiến trình):
  cd backend
  source .venv/bin/activate
  pytest -v --tb=long -s --cov=app --cov-report=term-missing

  Giải thích flags:
    -v                      : verbose — hiện tên từng test case
    --tb=long               : hiện full traceback khi test fail
    -s                      : hiện print() và logging trong quá trình test
    --cov=app               : đo coverage cho thư mục app/
    --cov-report=term-missing : hiện các dòng code chưa được test
```

```
Kết quả terminal mong đợi (Backend):
  ===================== test session starts =====================
  platform linux -- Python 3.12.3, pytest-8.2.2, pluggy-1.5.0
  collected 38 items

  tests/test_models.py::test_user_password_hash PASSED
  tests/test_models.py::test_user_to_dict_no_password PASSED
  tests/test_models.py::test_watchlist_unique_constraint PASSED
  tests/test_models.py::test_cascade_delete PASSED
  tests/test_auth.py::test_register_success PASSED
  tests/test_auth.py::test_register_duplicate_username PASSED
  tests/test_auth.py::test_register_short_password PASSED
  tests/test_auth.py::test_login_success PASSED
  tests/test_auth.py::test_login_wrong_password PASSED
  tests/test_account.py::test_change_username_no_auth PASSED
  tests/test_account.py::test_change_username_success PASSED
  tests/test_account.py::test_change_username_duplicate PASSED
  tests/test_account.py::test_change_username_wrong_password PASSED
  tests/test_account.py::test_change_password_success PASSED
  tests/test_account.py::test_change_password_same_as_current PASSED
  tests/test_account.py::test_change_password_wrong_current PASSED
  tests/test_account.py::test_delete_account_success PASSED
  tests/test_account.py::test_delete_account_wrong_password PASSED
  tests/test_account.py::test_token_invalid_after_delete PASSED
  tests/test_coins.py::test_get_coins_page1 PASSED
  tests/test_coins.py::test_get_coin_not_found PASSED
  tests/test_coins.py::test_search_coins PASSED
  tests/test_coins.py::test_search_case_insensitive PASSED
  tests/test_watchlist.py::test_get_watchlist_no_auth PASSED
  tests/test_watchlist.py::test_add_coin PASSED
  tests/test_watchlist.py::test_add_duplicate_coin PASSED
  tests/test_watchlist.py::test_delete_coin PASSED

  ----------- coverage: app/ -----------
  Name                       Stmts   Miss  Cover
  -----------------------------------------------
  app/__init__.py               25      2    92%
  app/models.py                 68      5    93%
  app/routes/auth.py            68      5    93%
  app/routes/coins.py           55      8    85%
  app/routes/news.py            28      3    89%
  app/routes/watchlist.py       38      3    92%
  app/services/coingecko.py     45      6    87%
  app/scheduler.py              32      4    88%
  -----------------------------------------------
  TOTAL                        359     36    90%

  ====================== 27 passed in 2.91s ======================
```

```
Lệnh chạy Frontend (đầy đủ output, không ẩn tiến trình):
  deactivate          ← Thoát .venv trước
  cd frontend
  pnpm run test -- --reporter=verbose

  Giải thích flags:
    --reporter=verbose : hiện tên từng test và kết quả chi tiết
```

```
Kết quả terminal mong đợi (Frontend):
   RUN  v1.x.x  /path/to/frontend

  tests/stores/auth.test.js
    auth store
      ✓ isAuthenticated returns false when no token (5ms)
      ✓ login action sets token and user (12ms)
      ✓ logout clears token and user from localStorage (3ms)
      ✓ isAuthenticated returns true after login (2ms)

  tests/components/CoinTable.test.js
    CoinTable
      ✓ renders coin name, symbol and price (18ms)
      ✓ shows add button when mode is default and authenticated (8ms)
      ✓ hides add button when not authenticated (4ms)
      ✓ shows delete button when mode is watchlist (6ms)
      ✓ navigates to coin detail on row click (9ms)

  tests/views/AccountSettings.test.js
    AccountSettingsView
      ✓ redirects to /auth if not logged in (6ms)
      ✓ shows error when confirm password does not match (7ms)
      ✓ calls logout and redirects on require_relogin response (14ms)
      ✓ shows per-section error without affecting other sections (8ms)

  Test Files  3 passed (3)
  Tests       13 passed (13)
  Duration    1.87s
```

**Kết quả mong đợi:** Tất cả test PASS, coverage backend ≥ 70%.

---

### Task 7.3: Deploy lên Railway

**Công việc:**

- Tạo `Procfile` ở thư mục gốc: `web: gunicorn --chdir backend run:app --bind 0.0.0.0:$PORT`
- Build frontend:
  ```bash
  deactivate        # ← Bắt buộc thoát .venv
  cd frontend
  pnpm run build    # Tạo frontend/dist/
  ```
- Cấu hình Flask serve Vue SPA: route catch-all trả `index.html` cho mọi path không phải `/api`
- `frontend/dist/` thêm vào `.gitignore` — Railway build lại khi deploy
- Railway start command: `flask db upgrade && gunicorn run:app`

> **Mẫu route catch-all trong Flask**:
> ```python
> @app.route('/', defaults={'path': ''})
> @app.route('/<path:path>')
> def serve_vue(path):
>     if path.startswith('api'):
>         return jsonify({'error': 'Not found'}), 404
>     # Trả index.html để Vue Router xử lý routing phía client
>     return send_from_directory(dist_folder, 'index.html')
> ```

**✅ Tiêu chuẩn chất lượng cần đảm bảo:**
- [ ] Build frontend sau `deactivate`
- [ ] `frontend/dist/` trong `.gitignore`
- [ ] `flask db upgrade` chạy tự động khi deploy
- [ ] Tất cả secrets set qua Railway environment variables

**🧪 Test case:**

```
Lệnh build + test local trước khi deploy:
  deactivate
  cd frontend && pnpm run build
  cd ../backend && source .venv/bin/activate
  FLASK_ENV=production python run.py
```

| # | Hành động | Kết quả mong đợi |
|---|-----------|-----------------|
| 1 | Build frontend | Terminal: `✓ built in Xs`, tạo thư mục `dist/` |
| 2 | Flask serve dist/ | `localhost:5000` hiện Vue app đầy đủ |
| 3 | Truy cập `/coin/bitcoin` trực tiếp | Flask trả `index.html`, Vue Router xử lý — **không** 404 |
| 4 | Deploy Railway | App accessible qua URL Railway |
| 5 | Kiểm tra migration | `flask db upgrade` chạy tự động, đủ 5 bảng |
| 6 | Test production | Auth, Coins, Charts, News, Watchlist đều hoạt động |
| 7 | Kiểm tra scheduler | Sau 30 phút, DB có bản ghi `price_history` mới |

---

## Tổng quan Timeline ước tính

| Giai đoạn | Nội dung                        | Thời gian ước tính |
| --------- | ------------------------------- | ------------------ |
| 1         | Khởi tạo dự án & môi trường     | 1 ngày             |
| 2         | Database & Models               | 1 ngày             |
| 3         | Authentication & Account API    | 1-2 ngày           |
| 4         | Coins, News, Watchlist API      | 2-3 ngày           |
| 5         | APScheduler                     | 1 ngày             |
| 6         | Frontend (8 views + components) | 6-8 ngày           |
| 7         | Polish, Test, Deploy            | 2-3 ngày           |
| **Tổng**  |                                 | **~14-18 ngày**    |

---

## Lưu ý quan trọng

> [!WARNING]
> **CoinGecko Free API** giới hạn ~10-30 call/phút. Luôn query DB trước, chỉ gọi API khi DB trống hoặc theo lịch scheduler.

> [!WARNING]
> **Tách biệt môi trường**: KHÔNG bao giờ chạy `pnpm`/`node` khi đang active `.venv`. Luôn `deactivate` trước khi làm việc với frontend.

> [!NOTE]
> **Thứ tự phát triển**: Backend (GĐ 1-5) → Frontend (GĐ 6) → Polish + Deploy (GĐ 7). Có thể song song từ GĐ 3 nếu muốn.

> [!NOTE]
> **pnpm lockfile**: Commit `pnpm-lock.yaml` vào git. Không dùng `npm`/`yarn` trong project — chỉ dùng `pnpm`.

> [!NOTE]
> **Lệnh test luôn hiển thị đầy đủ tiến trình**: Backend dùng `pytest -v --tb=long -s`, Frontend dùng `pnpm run test -- --reporter=verbose`. Không dùng flag `-q` (quiet) khi debug.