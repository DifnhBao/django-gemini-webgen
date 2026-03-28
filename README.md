# AI Website Builder

Ứng dụng web Django cho phép **tự động tạo website mini bằng AI (Google Gemini)** chỉ từ một từ khóa chủ đề. Mỗi tài khoản có thể quản lý, xem trực tiếp và xóa các website đã tạo.

---

## Cấu hình trước khi chạy

Tạo một file tên là `.env` ở thư mục gốc của project và điền API key của bạn vào:
Nếu đã có sẵn file `.env`, mở file điền API key của bạn:

```env
GOOGLE_GEMINI_API_KEY=your_api_key_here
```

> Lấy API key miễn phí tại [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## Chạy hệ thống bằng Docker Compose 

Không cần cài Python hay thư viện, Docker lo hết.

```bash
# Lần đầu: chạy migration
docker compose run --rm web python manage.py migrate

# Khởi động ứng dụng (chạy nền)
docker compose up -d --build
```

Truy cập tại: **http://localhost:8000**


> Lưu ý: Hệ thống đã tích hợp sẵn một service `cron` chạy ngầm. Service này sẽ tự động dọn dẹp các website đã bị xóa quá 7 ngày, mỗi 24 giờ một lần.

---

## Hướng dẫn sử dụng

### 1. Đăng ký & đăng nhập
Truy cập `/accounts/signup/` để tạo tài khoản, sau đó đăng nhập tại `/accounts/login/`.

### 2. Tạo website bằng AI
- Tại **Dashboard**, nhập chủ đề vào ô văn bản (ví dụ: `flight booking`, `restaurant menu`, `portfolio`).
- Nhấn **Generate** — Gemini sẽ tạo ra một trang HTML hoàn chỉnh.
- Website hiển thị ngay sau khi tạo xong.

### 3. Quản lý website
- Danh sách tất cả website hiển thị trên Dashboard.
- Nhấn **Xem website** để xem lại.
- Nhấn **Xóa** để ẩn website (xóa mềm). Dữ liệu giữ lại 7 ngày trước khi xóa vĩnh viễn.

---

## Danh sách URL

| URL | Chức năng |
|-----|-----------|
| `/` | Dashboard |
| `/website/<id>/` | Xem website đã tạo |
| `/accounts/signup/` | Đăng ký |
| `/accounts/login/` | Đăng nhập |
| `/accounts/logout/` | Đăng xuất |
| `/admin/` | Trang quản trị Django |