import os
from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.extensions import db, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    frontend_origins = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")

    CORS(
        app,
        resources={r"/api/*": {"origins": [x.strip() for x in frontend_origins]}},
        supports_credentials=True,
    )

    from backend.models.user import User
    from backend.models.location import Location
    from backend.models.prediction import Prediction
    from backend.models.alert import Alert
    from backend.models.environment_data import EnvironmentData

    from backend.routes.auth import auth_bp
    from backend.routes.location import location_bp
    from backend.routes.weather import weather_bp
    from backend.routes.prediction import prediction_bp
    from backend.routes.alert import alert_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(alert_bp)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def home():
        return jsonify({"message": "Flash Flood Prediction API", "status": "running"})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "healthy"})

    return app


if __name__ == "__main__":
    create_app().run(debug=True, host="127.0.0.1", port=5000)
