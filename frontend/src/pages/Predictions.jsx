import { useEffect, useState } from "react";
import { Activity, CloudRain, Droplets, Gauge, TriangleAlert } from "lucide-react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import { createPrediction, getLocations, getPredictions } from "../services/api";

function Predictions() {
  const [predictions, setPredictions] = useState([]);
  const [locations, setLocations] = useState([]);
  const [locationId, setLocationId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const [p, l] = await Promise.all([getPredictions(), getLocations()]);
      setPredictions(p.data.predictions);
      setLocations(l.data.locations);
      if (!locationId && l.data.locations[0]) setLocationId(String(l.data.locations[0].id));
    } catch (err) {
      setError(err.response?.data?.error || "Unable to load predictions");
    }
  };

  useEffect(() => { load(); }, []);

  const generate = async () => {
    if (!locationId) return;
    setLoading(true);
    setError("");
    try {
      await createPrediction(Number(locationId));
      await load();
    } catch (err) {
      setError(err.response?.data?.details || err.response?.data?.error || "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <Sidebar />
      <main className="main">
        <Navbar />
        <div className="content">
          <div className="page-header">
            <div>
              <h1>Flood Predictions</h1>
              <p>Your trained XGBoost/Random Forest model is called by the backend.</p>
            </div>
            <div className="prediction-action">
              <select className="page-select" value={locationId} onChange={(e) => setLocationId(e.target.value)}>
                {locations.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
              </select>
              <button className="primary-button" onClick={generate} disabled={loading || !locationId}>
                {loading ? "Predicting..." : "Run Prediction"}
              </button>
            </div>
          </div>

          {error && <div className="error-box">{error}</div>}

          <div className="prediction-grid">
            {predictions.map((prediction) => (
              <div className="prediction-card" key={prediction.id}>
                <div className="prediction-header">
                  <div><span>Location</span><h2>{prediction.location}</h2></div>
                  <TriangleAlert size={25} />
                </div>

                <div className="prediction-score">
                  <div><span>Flood Probability</span><strong>{prediction.flood_probability}%</strong></div>
                  <span className={`risk-badge ${prediction.risk_level.toLowerCase()}`}>{prediction.risk_level}</span>
                </div>

                <div className="prediction-progress">
                  <div style={{ width: `${prediction.flood_probability}%` }} />
                </div>

                <div className="prediction-features">
                  <div><CloudRain size={18} /><span>Rainfall</span><strong>{prediction.rainfall} mm</strong></div>
                  <div><Droplets size={18} /><span>Humidity</span><strong>{prediction.humidity}%</strong></div>
                  <div><Gauge size={18} /><span>Pressure</span><strong>{prediction.pressure} hPa</strong></div>
                </div>

                <div className="prediction-footer">
                  <Activity size={18} />
                  Generated {prediction.created_at ? new Date(prediction.created_at).toLocaleString() : ""}
                </div>
              </div>
            ))}
          </div>

          {predictions.length === 0 && <div className="empty-state">No predictions yet. Select a location and run one.</div>}
        </div>
      </main>
    </div>
  );
}

export default Predictions;
