# ============================================================
# run_skill.py
# File chính để chạy skill Daily-Weather-Brief
#
# Cách dùng:
#   python run_skill.py                    → dùng thành phố mặc định (Hà Nội)
#   python run_skill.py "Da Nang"          → nhập tên thành phố qua argument
#   python run_skill.py --days 5           → dự báo 5 ngày
#   python run_skill.py "Tokyo" --days 3   → Tokyo, dự báo 3 ngày
# ============================================================

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Bắt buộc dùng UTF-8 để in emoji và tiếng Việt đúng trên Windows
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Import các hàm gọi API từ file weather_api.py trong cùng thư mục
from weather_api import fetch_current_weather, fetch_forecast


# ============================================================
# ĐỌC CẤU HÌNH TỪ config.json
# ============================================================

def load_config() -> dict:
    """
    Đọc file config.json để lấy API key, thành phố mặc định, và các cài đặt khác.
    Nếu không tìm thấy file, dùng giá trị mặc định.
    """
    config_path = Path(__file__).parent / "config.json"

    if not config_path.exists():
        print("⚠️  Không tìm thấy config.json, dùng cài đặt mặc định.")
        return {}

    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# IN BÁO CÁO RA MÀN HÌNH
# ============================================================

def print_current_weather(data: dict, units: str = "metric"):
    """In thông tin thời tiết hiện tại ra terminal với định dạng dễ đọc."""
    unit_symbol = "°C" if units == "metric" else "°F"
    speed_symbol = "m/s" if units == "metric" else "mph"

    print()
    print("=" * 55)
    print(f"  🌤️  THỜI TIẾT HIỆN TẠI — {data['city_name']}, {data['country']}")
    print(f"  🕐  Cập nhật lúc: {data['updated_at']}")
    print("=" * 55)
    print(f"  🌡️  Nhiệt độ    : {data['temp']:.0f}{unit_symbol}  "
          f"(cảm giác như {data['feels_like']:.0f}{unit_symbol})")
    print(f"  📊  Cao / Thấp  : {data['temp_max']:.0f}{unit_symbol} / {data['temp_min']:.0f}{unit_symbol}")
    print(f"  ☁️  Mô tả       : {data['description']}")
    print(f"  💧  Độ ẩm       : {data['humidity']}%")
    print(f"  🌬️  Gió         : {data['wind_speed']:.1f} {speed_symbol} hướng {data['wind_direction']}")
    print(f"  👁️  Tầm nhìn    : {data['visibility']} km")
    print(f"  ☁️  Mây che phủ : {data['clouds']}%")
    print(f"  🌅  Mặt trời    : Mọc {data['sunrise']}  —  Lặn {data['sunset']}")
    print("=" * 55)


def print_forecast(forecast_days: list, units: str = "metric"):
    """In bảng dự báo nhiều ngày ra terminal."""
    unit_symbol = "°C" if units == "metric" else "°F"
    speed_symbol = "m/s" if units == "metric" else "mph"

    print()
    print(f"  📅  DỰ BÁO {len(forecast_days)} NGÀY TỚI")
    print("-" * 55)

    for day in forecast_days:
        # Hiển thị cảnh báo mưa nếu xác suất > 50%
        rain_warning = f"  🌧️ Khả năng mưa {day['max_pop']}%" if day["max_pop"] > 50 else ""

        print(f"  📆  {day['date']}")
        print(f"       🌡️  {day['temp_min']:.0f}{unit_symbol} – {day['temp_max']:.0f}{unit_symbol}  "
              f"|  {day['description']}")
        print(f"       💧  Độ ẩm {day['humidity_avg']}%  "
              f"|  🌬️  Gió {day['wind_speed_avg']:.1f} {speed_symbol}  "
              f"|  🌧️  Mưa {day['max_pop']}%"
              f"{rain_warning}")
        print()


# ============================================================
# LƯU BÁO CÁO RA FILE MARKDOWN VÀ HTML
# ============================================================

def _fill_template(template: str, current: dict, forecast_rows: str,
                   summary: str, unit_symbol: str, speed_symbol: str) -> str:
    """Điền dữ liệu vào template (dùng chung cho cả .md và .html)."""
    return (
        template
        .replace("{{city}}",          current["city_name"])
        .replace("{{country}}",       current["country"])
        .replace("{{updated_at}}",    current["updated_at"])
        .replace("{{temp}}",          f"{current['temp']:.0f}")
        .replace("{{feels_like}}",    f"{current['feels_like']:.0f}")
        .replace("{{temp_min}}",      f"{current['temp_min']:.0f}")
        .replace("{{temp_max}}",      f"{current['temp_max']:.0f}")
        .replace("{{description}}",   current["description"])
        .replace("{{humidity}}",      str(current["humidity"]))
        .replace("{{pressure}}",      str(current["pressure"]))
        .replace("{{wind_speed}}",    f"{current['wind_speed']:.1f}")
        .replace("{{wind_dir}}",      current["wind_direction"])
        .replace("{{visibility}}",    str(current["visibility"]))
        .replace("{{clouds}}",        str(current["clouds"]))
        .replace("{{sunrise}}",       current["sunrise"])
        .replace("{{sunset}}",        current["sunset"])
        .replace("{{forecast_rows}}", forecast_rows.strip())
        .replace("{{summary}}",       summary)
    )


def save_report(current: dict, forecast: list, city: str, units: str = "metric") -> Path:
    """
    Xuất báo cáo thời tiết ra 2 định dạng:
    - Markdown (.md)  — dễ đọc trong terminal / text editor
    - HTML    (.html) — giao diện đẹp, mở bằng trình duyệt
    Trả về đường dẫn file Markdown (dòng OUTPUT_FILE: vẫn trỏ vào .md).
    """
    unit_symbol  = "°C" if units == "metric" else "°F"
    speed_symbol = "m/s" if units == "metric" else "mph"

    # Tạo thư mục outputs/ nếu chưa có
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    # Tên file gốc theo thành phố và thời gian
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    safe_city = city.lower().replace(" ", "-").replace(",", "")
    base_name = f"weather-{safe_city}-{timestamp}"

    summary = _generate_summary(current, forecast, unit_symbol)

    # ── Markdown forecast rows ──────────────────────────────
    md_rows = ""
    for day in forecast:
        md_rows += (
            f"| {day['date']} "
            f"| {day['temp_min']:.0f}{unit_symbol} – {day['temp_max']:.0f}{unit_symbol} "
            f"| {day['description']} "
            f"| {day['humidity_avg']}% "
            f"| {day['wind_speed_avg']:.1f} {speed_symbol} "
            f"| {day['max_pop']}% |\n"
        )

    # ── HTML forecast rows ──────────────────────────────────
    html_rows = ""
    for day in forecast:
        pop = day["max_pop"]
        pop_class = "pop-high" if pop > 50 else ("pop-med" if pop > 20 else "pop-low")
        html_rows += (
            f'<div class="forecast-row">'
            f'<span class="forecast-date">{day["date"]}</span>'
            f'<span class="forecast-desc">{day["description"]}</span>'
            f'<span class="forecast-temps">'
            f'{day["temp_max"]:.0f}° <span class="t-min">/ {day["temp_min"]:.0f}°</span>'
            f'</span>'
            f'<span class="forecast-pop {pop_class}">{pop}%</span>'
            f'</div>\n'
        )

    # ── Lưu Markdown ───────────────────────────────────────
    md_template_path = Path(__file__).parent / "templates" / "report_template.md"
    md_template = (md_template_path.read_text(encoding="utf-8")
                   if md_template_path.exists()
                   else "# {{city}}, {{country}}\n\n{{forecast_rows}}\n\n{{summary}}")
    md_path = output_dir / f"{base_name}.md"
    md_path.write_text(
        _fill_template(md_template, current, md_rows, summary, unit_symbol, speed_symbol),
        encoding="utf-8"
    )

    # ── Lưu HTML ───────────────────────────────────────────
    html_template_path = Path(__file__).parent / "templates" / "report_template.html"
    if html_template_path.exists():
        html_template = html_template_path.read_text(encoding="utf-8")
        html_path = output_dir / f"{base_name}.html"
        html_path.write_text(
            _fill_template(html_template, current, html_rows, summary, unit_symbol, speed_symbol),
            encoding="utf-8"
        )
        print(f"   HTML : {html_path}")

    return md_path


def _generate_summary(current: dict, forecast: list, unit_symbol: str) -> str:
    """Tự động tạo câu tóm tắt thời tiết dựa trên dữ liệu."""
    max_pop = max((d["max_pop"] for d in forecast), default=0)

    summary = (
        f"Thời tiết tại {current['city_name']}: {current['description'].lower()}, "
        f"nhiệt độ {current['temp']:.0f}{unit_symbol} "
        f"(cảm giác như {current['feels_like']:.0f}{unit_symbol})."
    )

    if max_pop > 50:
        summary += f" ⚠️ Khả năng mưa lên đến {max_pop}% trong vài ngày tới — nhớ mang theo ô!"
    elif max_pop > 20:
        summary += f" Có thể có mưa rải rác ({max_pop}%), nên chuẩn bị ô phòng hờ."
    else:
        summary += " Không có mưa đáng kể trong thời gian tới."

    return summary


# ============================================================
# ĐIỂM KHỞI CHẠY CHÍNH
# ============================================================

def main():
    # --- Đọc tham số dòng lệnh ---
    parser = argparse.ArgumentParser(
        description="Daily Weather Brief — Tra cứu thời tiết và dự báo nhiều ngày"
    )
    parser.add_argument(
        "city",
        nargs="?",          # tham số không bắt buộc
        default=None,
        help="Tên thành phố (tiếng Anh). Mặc định lấy từ config.json"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=3,
        help="Số ngày dự báo (1-5, mặc định: 3)"
    )
    args = parser.parse_args()

    # --- Đọc cấu hình ---
    config = load_config()
    units = config.get("api", {}).get("units", "metric")
    lang  = config.get("api", {}).get("language", "vi")

    # --- Xác định thành phố ---
    # Ưu tiên: argument dòng lệnh > config.json > mặc định "Hanoi"
    if args.city:
        city = args.city
    else:
        city = config.get("location", {}).get("default_city", "Hanoi")

    # Nếu chạy mà không có argument, hỏi người dùng có muốn đổi thành phố không
    # (bọc try/except EOFError để không bị treo khi chạy từ môi trường không có stdin)
    if not args.city:
        print(f"\n🏙️  Thành phố mặc định: {city}")
        try:
            user_input = input("   Nhập tên thành phố khác (hoặc Enter để giữ nguyên): ").strip()
            if user_input:
                city = user_input
        except EOFError:
            pass  # Không có stdin (ví dụ: chạy từ Claude Code) → dùng thành phố mặc định

    # Giới hạn số ngày dự báo trong khoảng hợp lệ
    days = max(1, min(args.days, 5))

    # --- Gọi API và hiển thị kết quả ---
    try:
        # Lấy thời tiết hiện tại
        current = fetch_current_weather(city, units=units, lang=lang)
        print_current_weather(current, units)

        # Lấy dự báo nhiều ngày
        forecast = fetch_forecast(city, days=days, units=units, lang=lang)
        print_forecast(forecast, units)

        # Lưu báo cáo ra file Markdown
        output_path = save_report(current, forecast, city, units)
        print(f"✅ Báo cáo đã được lưu tại:\n   {output_path}")
        print(f"\nOUTPUT_FILE: {output_path}")

    except (ValueError, EnvironmentError, ConnectionError) as e:
        # Hiển thị lỗi thân thiện và thoát với mã lỗi 1
        print(f"\n{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
