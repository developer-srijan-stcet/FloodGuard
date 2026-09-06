# Flash Flood Predictor

Full-stack flash-flood prediction system with React/Vite, Flask, XGBoost, OpenWeather, Open-Meteo, CWC/NWDP river telemetry and Twilio WhatsApp alerts.

## Important: environmental data is automatic

The user only selects a location. The frontend does **not** ask for soil moisture, slope, elevation or river level.

The backend automatically obtains:

- Elevation: Open-Meteo / Copernicus DEM.
- Soil moisture: Open-Meteo ECMWF soil-moisture data, converted from m³/m³ to percentage.
- Slope: calculated from five nearby Open-Meteo DEM elevation points.
- River level: nearest available CWC/NWDP telemetry station from the configured 2026-2030 public resources.
- Weather/rainfall: OpenWeather.

If no nearby river telemetry station is available, the backend does not invent a river level. Prediction returns HTTP 424 until valid river-level data is available.

## Backend

From the project root:

```powershell
cd D:\Flash_Flood_Predictor_deploy
.\.venv\Scripts\Activate.ps1
python -m backend.app
```

Health check:

```text
http://127.0.0.1:5000/api/health
```

Expected:

```json
{"status":"healthy"}
```

## Fresh Python environment

Use 64-bit Python. Python 3.13 is recommended for maximum ML-package compatibility; Python 3.14 can also work with compatible wheels.

```powershell
cd D:\Flash_Flood_Predictor_deploy
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Frontend

From the project root you can now run:

```powershell
npm run frontend:install
npm run dev
```

Or directly:

```powershell
cd frontend
npm install
npm run dev
```

## Environment variables

Copy `.env.example` to `.env` and put your real OpenWeather/Twilio credentials there.

Never put OpenWeather or Twilio secrets in React/Vite `VITE_*` variables.

## Database

The default local database is:

```text
instance/flood_prediction.db
```

Tables created automatically:

- users
- locations
- environment_data
- predictions
- alerts

`db.create_all()` creates missing tables. It does not migrate an old schema. For a clean development reset, stop Flask and delete `instance/flood_prediction.db`, then start Flask again.

## ML

The existing model is kept at:

```text
ml/models/flood_model.pkl
```

It expects exactly these eight features:

```text
rainfall_1h
rainfall_3h
rainfall_6h
soil_moisture
slope
elevation
river_level
temperature
```

The backend supplies all eight automatically.

To retrain from the root:

```powershell
python -m ml.train
```
