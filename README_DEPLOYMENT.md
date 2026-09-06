# Flash Flood Predictor — deployment notes

## Architecture

React/Vite frontend
→ JWT
→ Flask REST API
→ PostgreSQL/SQLite
→ OpenWeather
→ `ml/models/flood_model.pkl`
→ Twilio WhatsApp

## Local setup

### Backend

From the project root:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
copy .env.example .env
python run.py
```

Backend:
`http://127.0.0.1:5000`

Health:
`http://127.0.0.1:5000/api/health`

### Frontend

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

Frontend:
`http://localhost:5173`

## Environment variables

Keep all OpenWeather, Twilio, Flask and JWT secrets in the backend `.env`.

Do not use `VITE_` for secrets. Vite exposes `VITE_*` variables to browser code.

## Model inputs

The trained model requires:

- rainfall_1h
- rainfall_3h
- rainfall_6h
- soil_moisture
- slope
- elevation
- river_level
- temperature

OpenWeather supplies the weather/temperature inputs. Soil moisture, slope, elevation and river level are stored with each monitored location. The frontend therefore does not send arbitrary model features directly.

The current implementation derives the 3h/6h rainfall values from the next forecast intervals returned by OpenWeather. If the training data defines those columns as historical accumulated rainfall, replace that aggregation with the exact historical/sensor source used for training.

## JWT flow

1. Register: `POST /api/auth/register`
2. Login: `POST /api/auth/login`
3. Frontend stores the returned access token and sends:
   `Authorization: Bearer <token>`
4. Protected API routes require JWT.
5. `/api/auth/me` validates the current token/user.

## Twilio WhatsApp

Set:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_API_KEY`
- `TWILIO_API_SECRET`
- `TWILIO_WHATSAPP_FROM`

Set `AUTO_ALERTS=true` only when WhatsApp is configured and tested.

The user phone stored at registration is used as the WhatsApp destination. Use E.164 format such as `+91...`.

The Twilio Sandbox is for testing. Production WhatsApp requires a properly configured/approved WhatsApp sender.

## Database

SQLite is suitable for local development.

For production use PostgreSQL and set `DATABASE_URL` to your provider's connection string.

This project currently calls `db.create_all()` on startup. For future schema changes, add Flask-Migrate/Alembic rather than relying on `create_all()`.

## Deployment

The repository includes `render.yaml` for a Render-style deployment and `backend/Dockerfile` for container deployment.

Recommended production split:

- Frontend: Vercel/Netlify/Render Static Site
- Backend: Render/Railway/Fly.io/container host
- Database: managed PostgreSQL

After the backend URL is known, set frontend:

`VITE_API_BASE_URL=https://YOUR-BACKEND-DOMAIN/api`

And set backend:

`FRONTEND_ORIGIN=https://YOUR-FRONTEND-DOMAIN`

## Security

Never commit `.env`.

If a real OpenWeather or Twilio credential has ever been exposed publicly, revoke/rotate it before production deployment.
