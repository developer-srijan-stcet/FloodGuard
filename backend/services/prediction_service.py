import os
import pickle
import pandas as pd


_model = None


MODEL_FEATURES = [
    "rainfall_1h",
    "rainfall_3h",
    "rainfall_6h",
    "soil_moisture",
    "slope",
    "elevation",
    "river_level",
    "temperature",
]


def load_model(model_path):
    global _model

    if _model is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

        with open(model_path, "rb") as file:
            _model = pickle.load(file)

    return _model


def get_risk_level(probability):
    if probability >= 80:
        return "EXTREME"
    if probability >= 60:
        return "HIGH"
    if probability >= 40:
        return "MODERATE"
    if probability >= 20:
        return "LOW"
    return "SAFE"


def predict_flood(model_path, features):
    model = load_model(model_path)

    required = list(getattr(model, "feature_names_in_", MODEL_FEATURES))
    missing = [name for name in required if name not in features]

    if missing:
        raise ValueError(f"Missing model features: {missing}")

    dataframe = pd.DataFrame(
        [{name: float(features[name]) for name in required}],
        columns=required
    )

    prediction = int(model.predict(dataframe)[0])

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(dataframe)[0]
        # Binary flood classifier: class 1 is the flood probability.
        classes = list(getattr(model, "classes_", [0, 1]))
        if 1 in classes:
            probability = float(probabilities[classes.index(1)] * 100)
        else:
            probability = float(max(probabilities) * 100)
    else:
        probability = 100.0 if prediction == 1 else 0.0

    probability = round(max(0.0, min(100.0, probability)), 2)

    return {
        "prediction": prediction,
        "flood_probability": probability,
        "risk_level": get_risk_level(probability),
        "features": {name: float(features[name]) for name in required}
    }
