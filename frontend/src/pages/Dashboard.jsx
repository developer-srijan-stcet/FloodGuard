import { useEffect, useState } from "react";
import { Activity, CloudRain, MapPin, TriangleAlert } from "lucide-react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import RiskCard from "../components/RiskCard";
import WeatherCard from "../components/WeatherCard";
import RainfallChart from "../components/RainfallChart";
import AlertCard from "../components/AlertCard";
import FloodMap from "../components/FloodMap";
import { getLocations, getPredictions, getAlerts, getWeather } from "../services/api";

function Dashboard() {
  const [locations, setLocations] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [weather, setWeather] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const [l, p, a] = await Promise.all([
          getLocations(),
          getPredictions(),
          getAlerts()
        ]);

        setLocations(l.data.locations);
        setPredictions(p.data.predictions);
        setAlerts(a.data.alerts);

        const first = l.data.locations[0];
        if (first) {
          const w = await getWeather(first.latitude, first.longitude);
          setWeather(w.data.weather);
        }
      } catch (err) {
        setError(err.response?.data?.error || "Unable to load dashboard");
      }
    };

    load();
  }, []);

  const latest = predictions[0];
  const rainfallData = weather?.forecast?.map((item) => ({
    time: item.time?.slice(11, 16) || "",
    rainfall: item.rainfall
  })) || [];

  const dashboardWeather = weather ? {
    city: weather.city,
    rainfall: weather.rainfall_1h,
    wind: weather.wind_speed,
    pressure: weather.pressure,
    humidity: weather.humidity
  } : null;

  return (
    <div className="app">
      <Sidebar />
      <main className="main">
        <Navbar />
        <div className="content">
          {error && <div className="error-box">{error}</div>}

          <div className="stats-grid">
            <StatCard title="Monitored Locations" value={locations.length} description="Your saved locations" icon={MapPin} />
            <StatCard title="Predictions" value={predictions.length} description="Prediction history" icon={Activity} />
            <StatCard title="Current Rainfall" value={weather ? `${weather.rainfall_1h} mm` : "—"} description="OpenWeather, last 1 hour" icon={CloudRain} />
            <StatCard title="Alerts" value={alerts.length} description="Saved notifications" icon={TriangleAlert} />
          </div>

          <div className="dashboard-grid">
            <div>
              <RiskCard probability={latest?.flood_probability ?? 0} />
              <RainfallChart data={rainfallData} />
            </div>

            <div>
              {dashboardWeather
                ? <WeatherCard weather={dashboardWeather} />
                : <div className="weather-card empty-state">Add a location to start monitoring weather.</div>}

              <div className="alerts-section">
                <h2>Recent Alerts</h2>
                {alerts.slice(0, 3).map((alert) => (
                  <AlertCard
                    key={alert.id}
                    title={`${alert.risk_level} Flood Risk`}
                    message={alert.message}
                    time={alert.created_at ? new Date(alert.created_at).toLocaleString() : ""}
                  />
                ))}
                {alerts.length === 0 && <p className="muted">No alerts yet.</p>}
              </div>
            </div>
          </div>

          <div className="map-section">
            <div className="section-header">
              <div><span>Flood Risk Map</span><h2>Monitored Regions</h2></div>
            </div>
            <FloodMap locations={locations} predictions={predictions} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
