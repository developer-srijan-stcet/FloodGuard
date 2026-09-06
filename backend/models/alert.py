from backend.extensions import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    prediction_id = db.Column(
        db.Integer,
        db.ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    message = db.Column(db.Text, nullable=False)
    risk_level = db.Column(db.String(30), nullable=False)
    alert_type = db.Column(db.String(50), default="WHATSAPP")
    whatsapp_sent = db.Column(db.Boolean, default=False)
    twilio_sid = db.Column(db.String(100))
    acknowledged = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
