from backend.extensions import db


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False, index=True)

    rainfall = db.Column(db.Float)
    rainfall_1h = db.Column(db.Float)
    rainfall_3h = db.Column(db.Float)
    rainfall_6h = db.Column(db.Float)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    wind_speed = db.Column(db.Float)

    soil_moisture = db.Column(db.Float)
    slope = db.Column(db.Float)
    elevation = db.Column(db.Float)
    river_level = db.Column(db.Float)

    prediction = db.Column(db.Integer)
    flood_probability = db.Column(db.Float)
    risk_level = db.Column(db.String(30))
    model_version = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)

    alerts = db.relationship(
        "Alert",
        backref="prediction",
        lazy=True,
        cascade="all, delete-orphan",
    )
