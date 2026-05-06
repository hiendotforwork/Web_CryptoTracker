# 🪙 Crypto Tracker - Project Rules

Tài liệu này định nghĩa các quy tắc bắt buộc đối với tất cả AI Agents tham gia dự án.

## 🛡️ Nguyên tắc an toàn & Tài nguyên
- **Thay đổi Database**: Mọi thao tác `flask db migrate` hoặc sửa file `models.py` PHẢI giải thích lý do cụ thể và chờ người dùng xác nhận
- **Thao tác Xóa**: Tuyệt đối không xóa file mà không giải thích lý do. Khi xóa, phải liệt kê danh sách các file/module bị ảnh hưởng
- **Giới hạn thực thi**: Tự điều chỉnh kế hoạch để hoàn thành trong tối đa 10 bước (`steps`). Ưu tiên các lệnh tối ưu tài nguyên trên Linux Mint.

## 💻 Quy trình viết Code (Workflow)
- **Incremental Code**: Tuyệt đối không sinh toàn bộ mã nguồn lớn trong một lần. Hãy chia nhỏ thành từng phần (ví dụ: từng Route, từng Component) để người dùng dễ kiểm soát.
- **Tiêu chuẩn Clean Code**:
  - Backend: Tuân thủ PEP 8, dùng Type Hinting cho Python 3.12.
  - Frontend: Composition API cho Vue 3, định nghĩa rõ ràng Props và Emits.
  - Luôn ưu tiên viết code dễ bảo trì hơn là code ngắn gọn.
- **Comment giáo dục**: Trước mỗi file, hàm đều thêm một comment giải thích ngắn gọn các câu hỏi: What, Why, How

## ⚙️ Thông số nghiệp vụ (Business Logic)
- **API Limits**: Giới hạn tần suất gọi API bên thứ ba (CoinGecko) là **15 lần/phút**. Hãy triển khai cơ chế cache hoặc scheduler phù hợp
- **Session Timeout**: Cấu hình JWT hoặc phiên đăng nhập tự động hết hạn sau **30 phút** không hoạt động
- **Tech Stack**: Flask (Backend), Vue 3 + Vite (Frontend), PostgreSQL (DB), PNPM (Package Manager).

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