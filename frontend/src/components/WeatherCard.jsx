import {
  CloudRain,
  Droplets,
  Wind,
  Gauge
} from "lucide-react";

function WeatherCard({ weather }) {

  return (
    <div className="weather-card">

      <div className="weather-title">

        <div>
          <p>Current Weather</p>
          <h2>{weather.city}</h2>
        </div>

        <CloudRain size={40} />

      </div>

      <div className="weather-grid">

        <div>
          <Droplets size={18} />
          <span>Rainfall</span>
          <strong>{weather.rainfall} mm</strong>
        </div>

        <div>
          <Wind size={18} />
          <span>Wind</span>
          <strong>{weather.wind} m/s</strong>
        </div>

        <div>
          <Gauge size={18} />
          <span>Pressure</span>
          <strong>{weather.pressure} hPa</strong>
        </div>

        <div>
          <span>Humidity</span>
          <strong>{weather.humidity}%</strong>
        </div>

      </div>

    </div>
  );
}

export default WeatherCard;