import { useEffect, useState } from "react";
import { CloudRain, Droplets, Wind, Gauge, Thermometer } from "lucide-react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import { getLocations, getWeather } from "../services/api";

function Weather() {
  const [locations, setLocations] = useState([]);
  const [locationId, setLocationId] = useState("");
  const [weather, setWeather] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getLocations()
      .then((response) => {
        const items = response.data.locations;
        setLocations(items);
        if (items[0]) setLocationId(String(items[0].id));
      })
      .catch((err) => setError(err.response?.data?.error || "Unable to load locations"));
  }, []);

  useEffect(() => {
    const location = locations.find((item) => String(item.id) === String(locationId));
    if (!location) return;

    getWeather(location.latitude, location.longitude)
      .then((response) => setWeather(response.data.weather))
      .catch((err) => setError(err.response?.data?.error || "Unable to fetch weather"));
  }, [locationId, locations]);

  return (
    <div className="app">
      <Sidebar />
      <main className="main">
        <Navbar />
        <div className="content">
          <div className="page-header">
            <div>
              <h1>Weather Monitoring</h1>
              <p>Live weather data from OpenWeather.</p>
            </div>
            <select className="page-select" value={locationId} onChange={(e) => setLocationId(e.target.value)}>
              {locations.map((location) => <option key={location.id} value={location.id}>{location.name}</option>)}
            </select>
          </div>

          {error && <div className="error-box">{error}</div>}

          {weather && (
            <>
              <div className="weather-main-card">
                <div>
                  <span>Current Weather</span>
                  <h1>{weather.city}</h1>
                  <p>{weather.weather}</p>
                </div>
                <div className="weather-temperature">
                  <CloudRain size={55} />
                  <strong>{weather.temperature}°C</strong>
                </div>
              </div>

              <div className="weather-details-grid">
                <div className="weather-detail-card"><CloudRain size={25} /><span>Rainfall (1h)</span><strong>{weather.rainfall_1h} mm</strong></div>
                <div className="weather-detail-card"><Droplets size={25} /><span>Humidity</span><strong>{weather.humidity}%</strong></div>
                <div className="weather-detail-card"><Wind size={25} /><span>Wind Speed</span><strong>{weather.wind_speed} m/s</strong></div>
                <div className="weather-detail-card"><Gauge size={25} /><span>Pressure</span><strong>{weather.pressure} hPa</strong></div>
                <div className="weather-detail-card"><Thermometer size={25} /><span>Temperature</span><strong>{weather.temperature}°C</strong></div>
              </div>

              <div className="chart-card weather-forecast">
                <div className="section-title">
                  <h2>Forecast Rainfall</h2>
                  <p>Next forecast intervals used to derive the model's 3h/6h rainfall inputs.</p>
                </div>
                <div className="forecast-list">
                  {weather.forecast?.map((item) => (
                    <div className="forecast-item" key={item.time}>
                      <span>{item.time}</span>
                      <strong>{item.rainfall} mm</strong>
                      <small>{item.temperature}°C</small>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {!weather && !error && <div className="empty-state">Add a location to view weather.</div>}
        </div>
      </main>
    </div>
  );
}

export default Weather;
