import { useEffect, useState } from "react";
import { TriangleAlert, CloudRain, CheckCircle } from "lucide-react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import { getAlerts } from "../services/api";

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getAlerts()
      .then((response) => setAlerts(response.data.alerts))
      .catch((err) => setError(err.response?.data?.error || "Unable to load alerts"));
  }, []);

  return (
    <div className="app">
      <Sidebar />
      <main className="main">
        <Navbar />
        <div className="content">
          <div className="page-header">
            <div>
              <h1>Flood Alerts</h1>
              <p>WhatsApp notifications generated for HIGH and EXTREME risk.</p>
            </div>
            <div className="model-status"><span className="status-dot"></span>Alert System Active</div>
          </div>

          {error && <div className="error-box">{error}</div>}

          <div className="alerts-page">
            {alerts.map((alert) => (
              <div className="alert-page-card" key={alert.id}>
                <div className="alert-page-icon">
                  {alert.risk_level === "HIGH" || alert.risk_level === "EXTREME"
                    ? <TriangleAlert size={25} />
                    : <CloudRain size={25} />}
                </div>
                <div className="alert-page-content">
                  <div className="alert-page-header">
                    <div>
                      <h2>{alert.risk_level} Flood Risk</h2>
                      <span>{alert.location || "Unknown location"}</span>
                    </div>
                    <span className={`risk-badge ${alert.risk_level.toLowerCase()}`}>{alert.risk_level}</span>
                  </div>
                  <p>{alert.message}</p>
                  <small>{alert.created_at ? new Date(alert.created_at).toLocaleString() : ""}</small>
                </div>
              </div>
            ))}
          </div>

          {alerts.length === 0 && <div className="empty-state">No alerts have been generated.</div>}

          <div className="alert-system-card">
            <CheckCircle size={25} />
            <div>
              <h3>Notification System</h3>
              <p>Automatic alerts are controlled by the backend AUTO_ALERTS setting.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Alerts;
