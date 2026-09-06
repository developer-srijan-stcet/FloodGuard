from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.config import Config
from backend.extensions import db
from backend.models.user import User
from backend.models.prediction import Prediction
from backend.models.alert import Alert
from backend.services.twilio_service import send_whatsapp


alert_bp = Blueprint("alert", __name__, url_prefix="/api/alerts")


def should_send_alert(risk_level):
    return risk_level in {"HIGH", "EXTREME"}


def _message(prediction):
    return (
        "FLASH FLOOD ALERT\n"
        f"Location: {prediction.location.name}\n"
        f"Risk Level: {prediction.risk_level}\n"
        f"Flood Probability: {prediction.flood_probability:.2f}%\n"
        "Please take necessary precautions."
    )


@alert_bp.post("/send/<int:prediction_id>")
@jwt_required()
def send_alert(prediction_id):
    user_id = int(get_jwt_identity())

    prediction = Prediction.query.filter_by(
        id=prediction_id,
        user_id=user_id
    ).first()

    if not prediction:
        return jsonify({"error": "Prediction not found"}), 404

    if not should_send_alert(prediction.risk_level):
        return jsonify({
            "message": "No alert required",
            "risk_level": prediction.risk_level
        })

    user = db.session.get(User, user_id)
    if not user or not user.phone:
        return jsonify({"error": "User WhatsApp number is not configured"}), 400

    message = _message(prediction)

    try:
        sid = send_whatsapp(
            Config.TWILIO_ACCOUNT_SID,
            Config.TWILIO_API_KEY,
            Config.TWILIO_API_SECRET,
            Config.TWILIO_WHATSAPP_FROM,
            user.phone,
            message,
            Config.TWILIO_AUTH_TOKEN
        )

        alert = Alert(
            user_id=user_id,
            prediction_id=prediction.id,
            message=message,
            risk_level=prediction.risk_level,
            sms_sent=True,
            twilio_sid=sid
        )

        db.session.add(alert)
        db.session.commit()

        return jsonify({
            "message": "WhatsApp alert sent",
            "risk_level": prediction.risk_level,
            "twilio_sid": sid
        })

    except Exception as exc:
        db.session.rollback()
        return jsonify({
            "error": "Failed to send WhatsApp alert",
            "details": str(exc)
        }), 500


@alert_bp.get("")
@jwt_required()
def get_alerts():
    user_id = int(get_jwt_identity())

    alerts = Alert.query.filter_by(
        user_id=user_id
    ).order_by(Alert.created_at.desc()).all()

    return jsonify({
        "alerts": [
            {
                "id": alert.id,
                "prediction_id": alert.prediction_id,
                "location": alert.prediction.location.name if alert.prediction else None,
                "message": alert.message,
                "risk_level": alert.risk_level,
                "sms_sent": alert.sms_sent,
                "twilio_sid": alert.twilio_sid,
                "created_at": alert.created_at.isoformat() if alert.created_at else None
            }
            for alert in alerts
        ]
    })
