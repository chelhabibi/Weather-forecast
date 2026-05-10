# Daily-Weather-Brief

Skill tra cứu thời tiết thực tế và dự báo nhiều ngày, tích hợp với **OpenWeatherMap API**. Xuất báo cáo Markdown lưu tự động vào thư mục `outputs/`.

Được xây dựng bằng Claude Code — BTVN Buổi 3.

---

## Tính Năng

- Thời tiết **hiện tại**: nhiệt độ, độ ẩm, gió, tầm nhìn, giờ mặt trời mọc/lặn
- **Dự báo** 1–5 ngày tới (mặc định 3 ngày)
- Mô tả thời tiết bằng **tiếng Việt**
- **Cảnh báo mưa** tự động khi xác suất > 50%
- Lưu báo cáo `.md` vào `outputs/`, tự xóa file cũ (giữ 10 file gần nhất)
- Không cần cài thêm thư viện — dùng `urllib` có sẵn trong Python

---

## Cấu Trúc File

```
Daily-Weather-Brief/
├── README.md                     # File này
├── SKILL.md                      # Định nghĩa skill cho Claude Code
├── config.json                   # Cấu hình: API key, thành phố mặc định
├── weather_api.py                # Hàm gọi OpenWeatherMap API
├── run_skill.py                  # File chạy chính
├── prompts/
│   └── daily_brief_prompt.txt    # Prompt hướng dẫn Claude tóm tắt thời tiết
├── templates/
│   └── report_template.md        # Template báo cáo Markdown
└── outputs/
    └── weather-*.md              # Báo cáo tự động (không commit)
```

---

## Yêu Cầu

- Python **3.8+**
- API key miễn phí từ [OpenWeatherMap](https://openweathermap.org/api)
- Kết nối Internet

---

## Cài Đặt

### Bước 1 — Lấy API key

1. Đăng ký tại **https://openweathermap.org/** (miễn phí)
2. Đăng nhập → tên tài khoản → **My API Keys**
3. Copy key mặc định (chuỗi 32 ký tự)

> ⚠️ Key mới cần **10–15 phút** để kích hoạt sau khi đăng ký.

### Bước 2 — Set API key

```powershell
# Dùng trong phiên hiện tại
$env:OPENWEATHERMAP_API_KEY = "your_key_here"

# Lưu vĩnh viễn (khuyến nghị)
[Environment]::SetEnvironmentVariable("OPENWEATHERMAP_API_KEY", "your_key_here", "User")
```

### Bước 3 — (Tuỳ chọn) Đổi thành phố mặc định

Mở `config.json`, sửa dòng:
```json
"default_city": "Hanoi"
```
Thành phố phải viết bằng **tiếng Anh**, ví dụ: `Da Nang`, `Ho Chi Minh City`, `Tokyo`.

---

## Cách Chạy

```powershell
# Di chuyển vào thư mục skill
cd "F:\khóa AI code\BTVN buổi 3\skills\Daily-Weather-Brief"

# Chạy với thành phố mặc định (Hanoi)
python run_skill.py

# Truyền thẳng tên thành phố
python run_skill.py "Hanoi"
python run_skill.py "Ho Chi Minh City"
python run_skill.py "Da Nang"

# Chọn số ngày dự báo (1–5, mặc định 3)
python run_skill.py "Hanoi" --days 5
python run_skill.py "Tokyo" --days 1
```

---

## Ví Dụ Output

```
=======================================================
  🌤️  THỜI TIẾT HIỆN TẠI — Hanoi, VN
  🕐  Cập nhật lúc: 10/05/2026 22:45
=======================================================
  🌡️  Nhiệt độ    : 31°C  (cảm giác như 36°C)
  📊  Cao / Thấp  : 33°C / 28°C
  ☁️  Mô tả       : Mây rải rác
  💧  Độ ẩm       : 72%
  🌬️  Gió         : 3.5 m/s hướng Đông Nam
  👁️  Tầm nhìn    : 10.0 km
  ☁️  Mây che phủ : 40%
  🌅  Mặt trời    : Mọc 05:31  —  Lặn 18:19
=======================================================

  📅  DỰ BÁO 3 NGÀY TỚI
-------------------------------------------------------
  📆  10/05/2026
       🌡️  28°C – 33°C  |  Mây rải rác
       💧  Độ ẩm 74%  |  🌬️  Gió 3.2 m/s  |  🌧️  Mưa 15%

  📆  11/05/2026
       🌡️  27°C – 32°C  |  Mưa nhẹ
       💧  Độ ẩm 82%  |  🌬️  Gió 4.1 m/s  |  🌧️  Mưa 68%
       🌧️ Khả năng mưa 68%

✅ Báo cáo đã được lưu tại:
   outputs\weather-hanoi-20260510-2245.md
```

File `.md` lưu tại `outputs/` có thể mở bằng bất kỳ trình đọc Markdown nào (VS Code, Obsidian, GitHub).

---

## Xử Lý Lỗi

| Lỗi | Nguyên nhân | Cách xử lý |
|-----|-------------|------------|
| `OPENWEATHERMAP_API_KEY is not set` | Chưa set biến môi trường | Chạy lệnh set ở Bước 2 |
| `API key không hợp lệ (401)` | Key sai hoặc chưa kích hoạt | Kiểm tra key; đợi 15 phút nếu mới đăng ký |
| `Không tìm thấy thành phố (404)` | Tên thành phố không đúng | Dùng tên tiếng Anh: `Hanoi`, `Da Nang` |
| `Vượt quá giới hạn (429)` | Quá 60 lượt/phút | Đợi 1 phút rồi thử lại |
| `Không thể kết nối` | Mất Internet | Kiểm tra kết nối mạng |

---

## Mô Tả Các File Code

### `weather_api.py`
Chứa 2 hàm chính:
- `fetch_current_weather(city)` — gọi endpoint `/weather`, trả về dict thời tiết hiện tại đã làm sạch
- `fetch_forecast(city, days)` — gọi endpoint `/forecast`, nhóm dữ liệu theo ngày, trả về list dự báo

Dùng `urllib` (thư viện chuẩn của Python, không cần `pip install`).

### `run_skill.py`
Entry point chính:
- Đọc cấu hình từ `config.json`
- Nhận tên thành phố từ dòng lệnh hoặc hỏi người dùng
- Gọi `weather_api.py` để lấy dữ liệu
- In kết quả ra terminal
- Điền dữ liệu vào `templates/report_template.md` và lưu vào `outputs/`

### `config.json`
Cấu hình tập trung: API key placeholder, thành phố mặc định, ngôn ngữ, đơn vị đo, số file output giữ lại.

---

## Giới Hạn Free Tier

OpenWeatherMap miễn phí cho phép:
- **60 lượt gọi/phút**
- **1.000.000 lượt/tháng**
- Dự báo tối đa **5 ngày**

Đủ dùng cho mục đích cá nhân và học tập.

---

*Python 3.8+ | Không cần thư viện ngoài | OpenWeatherMap Free Tier*
