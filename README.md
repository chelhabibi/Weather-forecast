# Daily-Weather-Brief

Skill tra cứu thời tiết thực tế + dự báo nhiều ngày qua **OpenWeatherMap API**. Xuất báo cáo **Markdown** và **HTML** (có giao diện đẹp, tìm kiếm thành phố trực tiếp trên browser).

---

## Cài đặt nhanh

**Bước 1 — Lấy API key miễn phí:**  
Đăng ký tại [openweathermap.org](https://openweathermap.org) → My API Keys → copy key 32 ký tự.

**Bước 2 — Set API key:**
```powershell
[Environment]::SetEnvironmentVariable("OPENWEATHERMAP_API_KEY", "your_key_here", "User")
```

**Bước 3 — Chạy:**
```powershell
python run_skill.py "Hanoi"
python run_skill.py "Ho Chi Minh City" --days 5
```

Báo cáo lưu vào `outputs/`. Mở file `.html` bằng trình duyệt để xem giao diện đẹp và tìm kiếm thành phố khác.

---

## Cấu trúc

```
Daily-Weather-Brief/
├── SKILL.md              # Định nghĩa skill cho Claude Code
├── run_skill.py          # Entry point chính
├── weather_api.py        # Gọi OpenWeatherMap API
├── config.json           # Cấu hình (thành phố mặc định, đơn vị)
├── install.ps1           # Cài skill vào ~/.claude/skills/
├── templates/
│   ├── report_template.md    # Template Markdown
│   └── report_template.html  # Template HTML (có city switcher)
├── prompts/
│   └── daily_brief_prompt.txt
└── outputs/              # Báo cáo được tạo ra
```

---

## Yêu cầu

- Python 3.8+ (không cần pip install thêm gì)
- API key miễn phí từ OpenWeatherMap
- Kết nối Internet

---

*BTVN Buổi 3 — Khoá AI Code*
