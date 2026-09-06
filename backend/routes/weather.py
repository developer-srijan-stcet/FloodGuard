from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.config import Config
from backend.services.weather_service import get_weather


weather_bp = Blueprint("weather", __name__, url_prefix="/api/weather")


@weather_bp.get("")
@jwt_required()
def weather():
    latitude = request.args.get("lat")
    longitude = request.args.get("lon")

    # Keep compatibility with the old frontend query names.
    latitude = latitude if latitude is not None else request.args.get("latitude")
    longitude = longitude if longitude is not None else request.args.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({"error": "lat and lon are required"}), 400

    try:
        weather_data = get_weather(
            Config.OPENWEATHER_API_KEY,
            float(latitude),
            float(longitude)
        )
        return jsonify({
            "latitude": float(latitude),
            "longitude": float(longitude),
            "weather": weather_data
        })
    except ValueError:
        return jsonify({"error": "Latitude and longitude must be numbers"}), 400
    except Exception:
        return jsonify({"error": "Unable to fetch weather"}), 502
