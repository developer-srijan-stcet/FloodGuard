from backend.extensions import db


class EnvironmentData(db.Model):
    __tablename__ = "environment_data"

    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(
        db.Integer,
        db.ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    elevation = db.Column(db.Float)
    slope = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)
    river_level = db.Column(db.Float)

    river_station_name = db.Column(db.String(200))
    river_name = db.Column(db.String(200))
    river_station_latitude = db.Column(db.Float)
    river_station_longitude = db.Column(db.Float)
    river_level_source = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
