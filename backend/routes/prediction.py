from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.config import Config
from backend.extensions import db
from backend.models.location import Location
from backend.models.prediction import Prediction
from backend.models.alert import Alert
from backend.models.user import User
from backend.services.weather_service import get_weather
from backend.services.environment_service import fetch_environment
from backend.services.prediction_service import predict_flood
from backend.services.twilio_service import send_whatsapp

prediction_bp = Blueprint("prediction", __name__, url_prefix="/api/predict")


def _build_message(prediction):
    return (
        "FLASH FLOOD ALERT\n"
        f"Location: {prediction.location.name}\n"
        f"Risk Level: {prediction.risk_level}\n"
        f"Flood Probability: {prediction.flood_probability:.2f}%\n"
        "Please take necessary precautions."
    )


def _auto_alert(user, prediction):
    if not Config.AUTO_ALERTS or prediction.risk_level not in {"HIGH", "EXTREME"}:
        return None
    if not user or not user.phone:
        return None

    message = _build_message(prediction)
    sid = send_whatsapp(
        Config.TWILIO_ACCOUNT_SID,
        Config.TWILIO_API_KEY,
        Config.TWILIO_API_SECRET,
        Config.TWILIO_WHATSAPP_FROM,
        user.phone,
        message,
        Config.TWILIO_AUTH_TOKEN,
    )

    db.session.add(Alert(
        user_id=user.id,
        prediction_id=prediction.id,
        message=message,
        risk_level=prediction.risk_level,
        alert_type="WHATSAPP",
        whatsapp_sent=True,
        twilio_sid=sid,
    ))
    return sid


@prediction_bp.post("")
@jwt_required()
def predict():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    location_id = data.get("location_id")

    if location_id is None:
        return jsonify({"error": "location_id is required"}), 400

    try:
        location_id = int(location_id)
    except (TypeError, ValueError):
        return jsonify({"error": "location_id must be an integer"}), 400

    location = Location.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return jsonify({"error": "Location not found"}), 404

    try:
        # Refresh environmental inputs automatically on every prediction.
        environment = fetch_environment(location.latitude, location.longitude, location.state)
        location.soil_moisture = environment["soil_moisture"]
        location.slope = environment["slope"]
        location.elevation = environment["elevation"]
        location.river_level = environment["river_level"]
        location.river_station_name = environment["river_station_name"]
        location.river_name = environment["river_name"]
        location.river_level_source = environment["river_level_source"]

        if environment["river_level"] is None:
            return jsonify({
                "error": "No nearby river-water-level telemetry station was found for this location.",
                "details": "The ML model requires river_level, so a prediction was not generated rather than inventing a value.",
                "environment": environment,
            }), 424

        weather = get_weather(Config.OPENWEATHER_API_KEY, location.latitude, location.longitude)

        features = {
            "rainfall_1h": weather["rainfall_1h"],
            "rainfall_3h": weather["rainfall_3h"],
            "rainfall_6h": weather["rainfall_6h"],
            "soil_moisture": environment["soil_moisture"],
            "slope": environment["slope"],
            "elevation": environment["elevation"],
            "river_level": environment["river_level"],
            "temperature": weather["temperature"],
        }

        result = predict_flood(Config.MODEL_PATH, features)
        model_version = "flood_model.pkl"

        prediction = Prediction(
            user_id=user_id,
            location_id=location.id,
            rainfall=weather["rainfall_1h"],
            rainfall_1h=weather["rainfall_1h"],
            rainfall_3h=weather["rainfall_3h"],
            rainfall_6h=weather["rainfall_6h"],
            temperature=weather["temperature"],
            humidity=weather["humidity"],
            pressure=weather["pressure"],
            wind_speed=weather["wind_speed"],
            soil_moisture=environment["soil_moisture"],
            slope=environment["slope"],
            elevation=environment["elevation"],
            river_level=environment["river_level"],
            prediction=result["prediction"],
            flood_probability=result["flood_probability"],
            risk_level=result["risk_level"],
            model_version=model_version,
        )
        db.session.add(prediction)
        db.session.flush()

        user = db.session.get(User, user_id)
        twilio_sid = _auto_alert(user, prediction)
        db.session.commit()

        return jsonify({
            "message": "Prediction successful",
            "prediction_id": prediction.id,
            "location": {
                "id": location.id,
                "name": location.name,
                "latitude": location.latitude,
                "longitude": location.longitude,
            },
            "weather": weather,
            "environment": environment,
            "result": result,
            "alert_sent": bool(twilio_sid),
        }), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Prediction failed", "details": str(exc)}), 400


@prediction_bp.get("/history")
@jwt_required()
def prediction_history():
    user_id = int(get_jwt_identity())
    predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.created_at.desc()).all()
    return jsonify({"predictions": [
        {
            "id": p.id,
            "location_id": p.location_id,
            "location": p.location.name if p.location else None,
            "rainfall": p.rainfall,
            "rainfall_1h": p.rainfall_1h,
            "rainfall_3h": p.rainfall_3h,
            "rainfall_6h": p.rainfall_6h,
            "temperature": p.temperature,
            "humidity": p.humidity,
            "pressure": p.pressure,
            "wind_speed": p.wind_speed,
            "soil_moisture": p.soil_moisture,
            "slope": p.slope,
            "elevation": p.elevation,
            "river_level": p.river_level,
            "prediction": p.prediction,
            "flood_probability": p.flood_probability,
            "risk_level": p.risk_level,
            "model_version": p.model_version,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in predictions
    ]})
