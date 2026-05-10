# ============================================================
# weather_api.py
# Chứa các hàm gọi API từ OpenWeatherMap
# Không cần cài thêm thư viện — dùng urllib có sẵn trong Python
# ============================================================

import json
import os
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta

# --- Địa chỉ gốc của OpenWeatherMap API ---
BASE_URL = "https://api.openweathermap.org/data/2.5"


# ============================================================
# HÀM PHỤ TRỢ
# ============================================================

def _get_api_key() -> str:
    """
    Lấy API key từ biến môi trường OPENWEATHERMAP_API_KEY.
    Nếu chưa set, báo lỗi rõ ràng để người dùng biết cần làm gì.
    """
    key = os.environ.get("OPENWEATHERMAP_API_KEY", "").strip()
    if not key:
        raise EnvironmentError(
            "\n❌ Chưa tìm thấy OPENWEATHERMAP_API_KEY!\n"
            "Hãy set API key bằng lệnh sau trong PowerShell:\n"
            "  $env:OPENWEATHERMAP_API_KEY = 'your_key_here'\n"
            "Lấy key miễn phí tại: https://openweathermap.org/api"
        )
    return key


def _call_api(endpoint: str, params: dict) -> dict:
    """
    Gọi một endpoint bất kỳ của OpenWeatherMap.
    Tự động gắn API key vào params trước khi gửi request.
    Xử lý các lỗi phổ biến và trả về thông báo dễ hiểu.
    """
    params["appid"] = _get_api_key()

    # Ghép URL đầy đủ từ base + endpoint + query string
    full_url = f"{BASE_URL}/{endpoint}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(full_url, timeout=10) as response:
            # Đọc và parse JSON từ response
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        # Đọc nội dung lỗi từ server để hiển thị cho người dùng
        error_body = e.read().decode("utf-8")

        if e.code == 401:
            raise ValueError(
                "❌ API key không hợp lệ (lỗi 401).\n"
                "Kiểm tra lại key hoặc đợi 15 phút nếu vừa đăng ký."
            ) from e

        if e.code == 404:
            city = params.get("q", "")
            raise ValueError(
                f"❌ Không tìm thấy thành phố: '{city}' (lỗi 404).\n"
                "Thử dùng tên tiếng Anh, ví dụ: 'Hanoi', 'Ho Chi Minh City', 'Da Nang'."
            ) from e

        if e.code == 429:
            raise ValueError(
                "❌ Vượt quá giới hạn gọi API (lỗi 429).\n"
                "Free tier cho phép 60 lượt/phút. Đợi 1 phút rồi thử lại."
            ) from e

        raise ValueError(f"❌ Lỗi API {e.code}: {error_body}") from e

    except urllib.error.URLError as e:
        raise ConnectionError(
            f"❌ Không thể kết nối tới OpenWeatherMap: {e.reason}\n"
            "Kiểm tra kết nối Internet của bạn."
        ) from e


def _deg_to_direction(deg: int) -> str:
    """
    Chuyển góc độ gió (0-360) thành hướng la bàn tiếng Việt.
    Ví dụ: 45 → 'Đông Bắc', 180 → 'Nam'
    """
    directions = [
        (0,   "Bắc"),
        (45,  "Đông Bắc"),
        (90,  "Đông"),
        (135, "Đông Nam"),
        (180, "Nam"),
        (225, "Tây Nam"),
        (270, "Tây"),
        (315, "Tây Bắc"),
        (360, "Bắc"),
    ]
    # Tìm hướng gần nhất với góc được cho
    closest = min(directions, key=lambda x: abs(x[0] - (deg % 360)))
    return closest[1]


def _unix_to_local_time(unix_ts: int, tz_offset_sec: int, fmt: str = "%H:%M") -> str:
    """
    Chuyển Unix timestamp thành giờ địa phương dạng chuỗi.
    tz_offset_sec: múi giờ địa phương tính bằng giây (lấy từ API)
    """
    tz = timezone(timedelta(seconds=tz_offset_sec))
    return datetime.fromtimestamp(unix_ts, tz=tz).strftime(fmt)


# ============================================================
# HÀM CHÍNH — GỌI API
# ============================================================

def fetch_current_weather(city: str, units: str = "metric", lang: str = "vi") -> dict:
    """
    Lấy thông tin thời tiết HIỆN TẠI của một thành phố.

    Trả về dict đã được làm sạch với các trường:
    - city_name, country
    - temp, feels_like (°C)
    - description (mô tả tiếng Việt)
    - humidity (%), pressure (hPa)
    - wind_speed (m/s), wind_direction (hướng)
    - visibility (km), clouds (%)
    - sunrise, sunset (giờ địa phương)
    - updated_at (thời điểm cập nhật)
    """
    print(f"🌍 Đang lấy thời tiết hiện tại cho: {city}...")

    # Gọi endpoint /weather
    raw = _call_api("weather", {"q": city, "units": units, "lang": lang})

    tz_offset = raw.get("timezone", 0)

    return {
        "city_name":     raw.get("name", city),
        "country":       raw.get("sys", {}).get("country", ""),
        "temp":          raw["main"]["temp"],
        "feels_like":    raw["main"]["feels_like"],
        "temp_min":      raw["main"]["temp_min"],
        "temp_max":      raw["main"]["temp_max"],
        "description":   raw["weather"][0]["description"].capitalize(),
        "humidity":      raw["main"]["humidity"],
        "pressure":      raw["main"]["pressure"],
        "wind_speed":    raw.get("wind", {}).get("speed", 0),
        "wind_direction": _deg_to_direction(raw.get("wind", {}).get("deg", 0)),
        "visibility":    round(raw.get("visibility", 0) / 1000, 1),  # đổi m → km
        "clouds":        raw.get("clouds", {}).get("all", 0),
        "sunrise":       _unix_to_local_time(raw["sys"]["sunrise"], tz_offset),
        "sunset":        _unix_to_local_time(raw["sys"]["sunset"], tz_offset),
        "updated_at":    _unix_to_local_time(raw["dt"], tz_offset, fmt="%d/%m/%Y %H:%M"),
        "tz_offset":     tz_offset,
    }


def fetch_forecast(city: str, days: int = 3, units: str = "metric", lang: str = "vi") -> list:
    """
    Lấy DỰ BÁO thời tiết nhiều ngày tới (tối đa 5 ngày).
    OpenWeatherMap trả về các mốc cách nhau 3 tiếng.

    days: số ngày muốn lấy dự báo (1-5)
    Trả về list, mỗi phần tử là một ngày với thông tin tổng hợp:
    - date (ngày dạng dd/mm/yyyy)
    - temp_min, temp_max (nhiệt độ thấp nhất/cao nhất trong ngày)
    - description (mô tả phổ biến nhất trong ngày)
    - humidity_avg (độ ẩm trung bình)
    - max_pop (xác suất mưa cao nhất, %)
    - wind_speed_avg (tốc độ gió trung bình)
    """
    print(f"📅 Đang lấy dự báo {days} ngày tới cho: {city}...")

    # cnt = số mốc cần lấy (mỗi ngày có 8 mốc × 3h = 24h)
    cnt = days * 8
    raw = _call_api("forecast", {"q": city, "cnt": cnt, "units": units, "lang": lang})

    tz_offset = raw.get("city", {}).get("timezone", 0)
    tz = timezone(timedelta(seconds=tz_offset))

    # --- Nhóm các mốc theo ngày ---
    days_map = {}  # key: "dd/mm/yyyy", value: list các mốc trong ngày đó

    for slot in raw.get("list", []):
        slot_dt = datetime.fromtimestamp(slot["dt"], tz=tz)
        day_key = slot_dt.strftime("%d/%m/%Y")

        if day_key not in days_map:
            days_map[day_key] = []
        days_map[day_key].append(slot)

    # --- Tổng hợp thông tin từng ngày ---
    forecast_days = []

    for day_key, slots in days_map.items():
        temps       = [s["main"]["temp"] for s in slots]
        humidities  = [s["main"]["humidity"] for s in slots]
        wind_speeds = [s.get("wind", {}).get("speed", 0) for s in slots]
        pops        = [s.get("pop", 0) for s in slots]  # probability of precipitation (0-1)
        descriptions = [s["weather"][0]["description"] for s in slots]

        # Lấy mô tả phổ biến nhất trong ngày
        most_common_desc = max(set(descriptions), key=descriptions.count).capitalize()

        forecast_days.append({
            "date":          day_key,
            "temp_min":      round(min(temps), 1),
            "temp_max":      round(max(temps), 1),
            "description":   most_common_desc,
            "humidity_avg":  round(sum(humidities) / len(humidities)),
            "wind_speed_avg": round(sum(wind_speeds) / len(wind_speeds), 1),
            "max_pop":       round(max(pops) * 100),  # đổi 0-1 thành %
        })

    return forecast_days
