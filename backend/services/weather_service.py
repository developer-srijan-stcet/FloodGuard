import requests


CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"


def _require_key(api_key):
    if not api_key:
        raise RuntimeError("OPENWEATHER_API_KEY is not configured")


def search_location(api_key, city):
    _require_key(api_key)

    response = requests.get(
        GEOCODING_URL,
        params={"q": city, "limit": 5, "appid": api_key},
        timeout=10
    )
    response.raise_for_status()

    return [
        {
            "name": item.get("name"),
            "state": item.get("state"),
            "country": item.get("country"),
            "latitude": item.get("lat"),
            "longitude": item.get("lon")
        }
        for item in response.json()
    ]


def _rain_from_forecast(item):
    rain = item.get("rain") or {}
    return float(rain.get("3h", 0) or 0)


def get_weather(api_key, latitude, longitude):
    _require_key(api_key)

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "units": "metric"
    }

    current_response = requests.get(
        CURRENT_URL, params=params, timeout=10
    )
    current_response.raise_for_status()
    current = current_response.json()

    forecast_response = requests.get(
        FORECAST_URL, params=params, timeout=10
    )
    forecast_response.raise_for_status()
    forecast = forecast_response.json()

    current_rainfall_1h = float(
        (current.get("rain") or {}).get("1h", 0) or 0
    )

    forecast_items = forecast.get("list", [])
    next_3h = sum(_rain_from_forecast(item) for item in forecast_items[:1])
    next_6h = sum(_rain_from_forecast(item) for item in forecast_items[:2])

    weather = current.get("weather", [{}])[0]

    return {
        "city": current.get("name"),
        "temperature": float(current["main"]["temp"]),
        "humidity": float(current["main"]["humidity"]),
        "pressure": float(current["main"]["pressure"]),
        "rainfall": current_rainfall_1h,
        "rainfall_1h": current_rainfall_1h,
        "rainfall_3h": round(next_3h, 2),
        "rainfall_6h": round(next_6h, 2),
        "wind_speed": float(current.get("wind", {}).get("speed", 0)),
        "weather": weather.get("description", "Unknown"),
        "icon": weather.get("icon"),
        "forecast": [
            {
                "time": item.get("dt_txt"),
                "rainfall": round(_rain_from_forecast(item), 2),
                "temperature": item.get("main", {}).get("temp")
            }
            for item in forecast_items[:8]
        ]
    }
