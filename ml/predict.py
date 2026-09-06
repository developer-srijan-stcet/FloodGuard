import pickle
import pandas as pd

from ml.config import FEATURES, MODEL_PATH


def load_model():

    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)

    return model


def predict_flood(
    rainfall_1h,
    rainfall_3h,
    rainfall_6h,
    soil_moisture,
    slope,
    elevation,
    river_level,
    temperature
):

    model = load_model()

    data = pd.DataFrame([{
        "rainfall_1h": rainfall_1h,
        "rainfall_3h": rainfall_3h,
        "rainfall_6h": rainfall_6h,
        "soil_moisture": soil_moisture,
        "slope": slope,
        "elevation": elevation,
        "river_level": river_level,
        "temperature": temperature
    }], columns=FEATURES)

    prediction = model.predict(data)[0]

    probability = float(
        model.predict_proba(data)[0][1] * 100
    )

    probability = round(probability, 2)

    if probability < 30:
        risk = "LOW"
    elif probability < 60:
        risk = "MODERATE"
    elif probability < 80:
        risk = "HIGH"
    else:
        risk = "EXTREME"

    return {
        "flood_prediction": int(prediction),
        "flood_probability": probability,
        "risk_level": risk
    }


if __name__ == "__main__":

    result = predict_flood(
        rainfall_1h=0,
        rainfall_3h=0,
        rainfall_6h=0,
        soil_moisture=20,
        slope=5,
        elevation=50,
        river_level=0.2,
        temperature=30
    )

    print("\nDry Condition Prediction:")
    print(result)