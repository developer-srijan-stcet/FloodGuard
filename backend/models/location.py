from backend.extensions import db


class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    name = db.Column(db.String(150), nullable=False)
    state = db.Column(db.String(150))
    country = db.Column(db.String(100))

    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # Latest automatically fetched environmental values.
    soil_moisture = db.Column(db.Float)
    slope = db.Column(db.Float)
    elevation = db.Column(db.Float)
    river_level = db.Column(db.Float)

    river_station_name = db.Column(db.String(200))
    river_name = db.Column(db.String(200))
    river_level_source = db.Column(db.String(500))
    environment_updated_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    predictions = db.relationship(
        "Prediction",
        backref="location",
        lazy=True,
        cascade="all, delete-orphan",
    )

    environment_history = db.relationship(
        "EnvironmentData",
        backref="location",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="EnvironmentData.created_at.desc()",
    )
