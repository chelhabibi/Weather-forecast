---
name: daily-weather-brief
description: "This skill should be used when the user asks for a weather brief, daily weather report, weather summary, weather forecast, thời tiết hôm nay, báo cáo thời tiết, check weather in, give me weather for a city, dự báo thời tiết, thời tiết tại."
version: 1.0.0
argument-hint: "[tên thành phố]"
allowed-tools: [Bash, Write, Read]
---

# Daily Weather Brief

## Giới Thiệu

**Daily Weather Brief** là một Claude Code skill giúp tra cứu thời tiết thực tế và dự báo nhiều ngày tới cho bất kỳ thành phố nào trên thế giới. Skill kết nối trực tiếp với **OpenWeatherMap API** và xuất báo cáo ra 2 định dạng: **Markdown** và **HTML** đẹp.

Sau khi chạy, skill tự động:
- Lấy điều kiện thời tiết hiện tại (nhiệt độ, độ ẩm, gió, tầm nhìn, v.v.)
- Lấy dự báo 1–5 ngày tới (mặc định 3 ngày)
- Xuất báo cáo `.md` và `.html` lưu vào thư mục `outputs/`

---

## Cách Lấy API Key OpenWeatherMap

### Bước 1 — Đăng ký tài khoản
1. Truy cập: **https://openweathermap.org/**
2. Nhấn **Sign Up** → điền email và mật khẩu → xác nhận email

### Bước 2 — Lấy API Key
1. Đăng nhập → nhấn tên tài khoản → **My API Keys**
2. Copy key mặc định (chuỗi 32 ký tự)

> **Lưu ý:** API key mới cần **10 phút – 2 tiếng** để kích hoạt. Nếu gặp lỗi 401, hãy đợi và thử lại.

### Bước 3 — Cài đặt API Key
```powershell
# Lưu vĩnh viễn (khuyến nghị)
[Environment]::SetEnvironmentVariable("OPENWEATHERMAP_API_KEY", "your_key_here", "User")

# Dùng trong phiên hiện tại
$env:OPENWEATHERMAP_API_KEY = "your_key_here"
```

---

## Hướng Dẫn Sử Dụng

### Cách chạy
```powershell
cd "path\to\Daily-Weather-Brief"

# Thành phố mặc định (Hanoi)
python run_skill.py

# Truyền thẳng tên thành phố
python run_skill.py "Hanoi"
python run_skill.py "Ho Chi Minh City"
python run_skill.py "Da Nang"

# Chọn số ngày dự báo (1–5, mặc định 3)
python run_skill.py "Tokyo" --days 5
```

### Thay đổi thành phố mặc định
Mở `config.json` và sửa trường `default_city`:
```json
{ "location": { "default_city": "Da Nang" } }
```

---

## Input / Output

### Input
| Tham số | Bắt buộc | Mô tả |
|---------|----------|-------|
| `city` | Không | Tên thành phố tiếng Anh (ví dụ: `Hanoi`, `Tokyo`) |
| `--days` | Không | Số ngày dự báo, 1–5, mặc định 3 |

### Output
Mỗi lần chạy tạo ra 2 file trong `outputs/`:
- `weather-hanoi-20260510-1430.md` — báo cáo Markdown
- `weather-hanoi-20260510-1430.html` — báo cáo HTML giao diện đẹp

---

## Xử Lý Lỗi Thường Gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|-----|-------------|------------|
| `OPENWEATHERMAP_API_KEY is not set` | Chưa set biến môi trường | Set theo hướng dẫn ở trên |
| `Invalid API key` (401) | Key chưa kích hoạt hoặc sai | Đợi tối đa 2 tiếng nếu key mới |
| `City not found` (404) | Tên thành phố không đúng | Dùng tên tiếng Anh: `Hanoi`, `Da Nang` |
| `Rate limit exceeded` (429) | Quá 60 lượt/phút | Đợi 1 phút rồi thử lại |

---

_API: OpenWeatherMap Free Tier | Python 3.8+ | Không cần thư viện ngoài_
