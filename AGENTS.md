# 🪙 Crypto Tracker - Project Rules

Tài liệu này định nghĩa các quy tắc bắt buộc đối với tất cả AI Agents tham gia dự án.

## 🛡️ Nguyên tắc an toàn & Tài nguyên
- **Thay đổi Database**: Mọi thao tác `flask db migrate` hoặc sửa file `models.py` PHẢI giải thích lý do cụ thể và chờ người dùng xác nhận
- **Thao tác Xóa**: Tuyệt đối không xóa file mà không giải thích lý do. Khi xóa, phải liệt kê danh sách các file/module bị ảnh hưởng
- **Giới hạn thực thi**: Tự điều chỉnh kế hoạch để hoàn thành trong tối đa 15 bước (`steps`). Ưu tiên các lệnh tối ưu tài nguyên trên Linux Mint.

## 💻 Quy trình viết Code (Workflow)
- **Incremental Code**: Tuyệt đối không sinh toàn bộ mã nguồn lớn trong một lần. Hãy chia nhỏ thành từng phần (ví dụ: từng Route, từng Component) để người dùng dễ kiểm soát.
- **Tiêu chuẩn Clean Code**:
  - Backend: Tuân thủ PEP 8, dùng Type Hinting cho Python 3.12.
  - Frontend: Composition API cho Vue 3, định nghĩa rõ ràng Props và Emits.
  - Luôn ưu tiên viết code dễ bảo trì hơn là code ngắn gọn.
- **Comment giáo dục**: Trước mỗi file, hàm đều thêm một comment giải thích ngắn gọn các câu hỏi bằng tiếng Việt: What, Why, How

## ⚙️ Thông số nghiệp vụ (Business Logic)
- **API Limits**: Giới hạn tần suất gọi API bên thứ ba (CoinGecko) là **15 lần/phút**. Hãy triển khai cơ chế cache hoặc scheduler phù hợp
- **Session Timeout**: Cấu hình JWT hoặc phiên đăng nhập tự động hết hạn sau **30 phút** không hoạt động
- **Tech Stack**: Flask (Backend), Vue 3 + Vite (Frontend), PostgreSQL (DB), PNPM (Package Manager).

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

## 📂 Chỉ dẫn cấu trúc
Tham khảo cấu trúc thư mục tại `README.md` để đảm bảo đặt file đúng vị trí (ví dụ: store trong `frontend/src/stores/`).

## Quy trình làm việc với các lệnh terminal cơ bản
**Khi làm việc với backend**
```bash
# Kích hoạt môi trường ảo Python TRƯỚC KHI chạy bất kỳ lệnh Flask/pip nào
cd backend
source .venv/bin/activate        # Linux/macOS
 
# Kiểm tra môi trường đúng chưa (phải thấy đường dẫn .venv)
which python   # → .../backend/.venv/bin/python
```

**Khi làm việc với frontend**
```bash
# Kiểm tra đã thoát chưa: dòng terminal không còn tiền tố (.venv)
cd frontend
# ⛔ PHẢI THOÁT môi trường ảo Python TRƯỚC KHI chạy pnpm/node
deactivate     # Thoát .venv nếu đang active
pnpm install   # hoặc pnpm run dev / pnpm run build
```