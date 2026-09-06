from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FEATURES = [
    "rainfall_1h",
    "rainfall_3h",
    "rainfall_6h",
    "soil_moisture",
    "slope",
    "elevation",
    "river_level",
    "temperature",
]
TARGET = "flood"
MODEL_PATH = str(BASE_DIR / "ml" / "models" / "flood_model.pkl")
DATA_PATH = str(BASE_DIR / "ml" / "data" / "flood_data.csv")
