# 🌤️ Báo Cáo Thời Tiết — {{city}}, {{country}}
_Cập nhật lúc: {{updated_at}}_

---

## 🌡️ Điều Kiện Hiện Tại

| Chỉ số | Giá trị |
|--------|---------|
| Nhiệt độ | {{temp}}°C (cảm giác như {{feels_like}}°C) |
| Mô tả | {{description}} |
| Độ ẩm | {{humidity}}% |
| Áp suất | {{pressure}} hPa |
| Tốc độ gió | {{wind_speed}} m/s hướng {{wind_dir}} |
| Tầm nhìn | {{visibility}} km |
| Mây che phủ | {{clouds}}% |
| 🌅 Mặt trời mọc | {{sunrise}} |
| 🌇 Mặt trời lặn | {{sunset}} |

---

## 📅 Dự Báo Các Ngày Tới

| Ngày | Nhiệt độ | Mô tả | Độ ẩm TB | Gió TB | 🌧️ Mưa |
|------|----------|-------|----------|--------|--------|
{{forecast_rows}}

---

## 📝 Tóm Tắt

{{summary}}

---
_Nguồn dữ liệu: OpenWeatherMap API | Skill: Daily-Weather-Brief v1.0.0_
