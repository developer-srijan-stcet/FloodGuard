from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.config import Config
from backend.extensions import db
from backend.models.location import Location
from backend.models.environment_data import EnvironmentData
from backend.services.weather_service import search_location
from backend.services.environment_service import fetch_environment


location_bp = Blueprint("location", __name__, url_prefix="/api")


def _location_json(loc):
    return {
        "id": loc.id,
        "name": loc.name,
        "state": loc.state,
        "country": loc.country,
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "soil_moisture": loc.soil_moisture,
        "slope": loc.slope,
        "elevation": loc.elevation,
        "river_level": loc.river_level,
        "river_station_name": loc.river_station_name,
        "river_name": loc.river_name,
        "river_level_source": loc.river_level_source,
        "environment_updated_at": loc.environment_updated_at.isoformat() if loc.environment_updated_at else None,
        "created_at": loc.created_at.isoformat() if loc.created_at else None,
    }


@location_bp.get("/location/search")
def location_search():
    city = (request.args.get("city") or "").strip()
    if not city:
        return jsonify({"error": "city parameter is required"}), 400

    try:
        return jsonify({"locations": search_location(Config.OPENWEATHER_API_KEY, city)})
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({
        "error": "Unable to search location",
        "details": str(exc)
    }), 502


@location_bp.get("/locations")
@jwt_required()
def get_locations():
    user_id = int(get_jwt_identity())
    locations = Location.query.filter_by(user_id=user_id).order_by(Location.created_at.desc()).all()
    return jsonify({"locations": [_location_json(loc) for loc in locations]})


@location_bp.post("/locations")
@jwt_required()
def create_location():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    required = ["name", "latitude", "longitude"]
    missing = [key for key in required if data.get(key) in (None, "")]
    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400

    try:
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        if not (-90 <= latitude <= 90):
            raise ValueError("Invalid latitude")
        if not (-180 <= longitude <= 180):
            raise ValueError("Invalid longitude")

        environment = fetch_environment(
            latitude,
            longitude,
            data.get("state"),
        )

        location = Location(
            user_id=user_id,
            name=str(data["name"]).strip(),
            state=data.get("state"),
            country=data.get("country"),
            latitude=latitude,
            longitude=longitude,
            soil_moisture=environment["soil_moisture"],
            slope=environment["slope"],
            elevation=environment["elevation"],
            river_level=environment["river_level"],
            river_station_name=environment["river_station_name"],
            river_name=environment["river_name"],
            river_level_source=environment["river_level_source"],
            environment_updated_at=datetime.now(timezone.utc),
        )
        db.session.add(location)
        db.session.flush()

        history = EnvironmentData(
            location_id=location.id,
            elevation=environment["elevation"],
            slope=environment["slope"],
            soil_moisture=environment["soil_moisture"],
            river_level=environment["river_level"],
            river_station_name=environment["river_station_name"],
            river_name=environment["river_name"],
            river_station_latitude=environment["river_station_latitude"],
            river_station_longitude=environment["river_station_longitude"],
            river_level_source=environment["river_level_source"],
        )
        db.session.add(history)
        db.session.commit()

        response = _location_json(location)
        response["environment"] = environment
        return jsonify({"message": "Location created with automatic environmental data", "location": response}), 201

    except (TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        db.session.rollback()
        return jsonify({
            "error": "Unable to fetch environmental data for this location",
            "details": str(exc),
        }), 502


@location_bp.post("/locations/<int:location_id>/refresh-environment")
@jwt_required()
def refresh_environment(location_id):
    user_id = int(get_jwt_identity())
    location = Location.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return jsonify({"error": "Location not found"}), 404

    try:
        environment = fetch_environment(location.latitude, location.longitude, location.state)
        now = datetime.now(timezone.utc)
        location.soil_moisture = environment["soil_moisture"]
        location.slope = environment["slope"]
        location.elevation = environment["elevation"]
        location.river_level = environment["river_level"]
        location.river_station_name = environment["river_station_name"]
        location.river_name = environment["river_name"]
        location.river_level_source = environment["river_level_source"]
        location.environment_updated_at = now

        db.session.add(EnvironmentData(
            location_id=location.id,
            elevation=environment["elevation"],
            slope=environment["slope"],
            soil_moisture=environment["soil_moisture"],
            river_level=environment["river_level"],
            river_station_name=environment["river_station_name"],
            river_name=environment["river_name"],
            river_station_latitude=environment["river_station_latitude"],
            river_station_longitude=environment["river_station_longitude"],
            river_level_source=environment["river_level_source"],
        ))
        db.session.commit()
        return jsonify({"message": "Environmental data refreshed", "environment": environment, "location": _location_json(location)})
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": "Unable to refresh environmental data", "details": str(exc)}), 502


@location_bp.delete("/locations/<int:location_id>")
@jwt_required()
def delete_location(location_id):
    user_id = int(get_jwt_identity())
    location = Location.query.filter_by(id=location_id, user_id=user_id).first()
    if not location:
        return jsonify({"error": "Location not found"}), 404

    db.session.delete(location)
    db.session.commit()
    return jsonify({"message": "Location deleted"})
