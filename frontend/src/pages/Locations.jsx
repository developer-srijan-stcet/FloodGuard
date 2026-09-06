import { useEffect, useState } from "react";
import {
  Activity,
  CloudRain,
  MapPin,
  RefreshCw,
  Trash2,
} from "lucide-react";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import FloodMap from "../components/FloodMap";

import {
  createLocation,
  deleteLocation,
  getLocations,
  searchLocations,
  createPrediction,
  refreshEnvironment,
  getPredictions,
} from "../services/api";

function Locations() {
  const [locations, setLocations] = useState([]);
  const [predictions, setPredictions] = useState([]);

  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);

  const [selected, setSelected] = useState(null);

  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(null);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const [locationsResponse, predictionsResponse] =
        await Promise.all([
          getLocations(),
          getPredictions(),
        ]);

      setLocations(locationsResponse.data.locations || []);
      setPredictions(predictionsResponse.data.predictions || []);
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Unable to load locations"
      );
    }
  };

  useEffect(() => {
    load();
  }, []);

  const findCity = async () => {
    const query = search.trim();

    if (!query) {
      setResults([]);
      return;
    }

    setError("");
    setMessage("");

    try {
      const response = await searchLocations(query);

      const found = response.data.locations || [];

      setResults(found);

      if (!found.length) {
        setMessage("No locations found.");
      }
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Location search failed"
      );
    }
  };

  const add = async () => {
    if (!selected) return;

    setLoading(true);
    setError("");

    setMessage(
      "Fetching weather, elevation, soil moisture, slope and river telemetry..."
    );

    try {
      await createLocation({
        name: selected.name,
        state: selected.state,
        country: selected.country,
        latitude: selected.latitude,
        longitude: selected.longitude,
      });

      setMessage(
        "Location added. Environmental data was fetched automatically."
      );

      setSelected(null);
      setResults([]);
      setSearch("");

      await load();
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Unable to add location"
      );

      if (err.response?.data?.details) {
        setMessage(err.response.data.details);
      }
    } finally {
      setLoading(false);
    }
  };

  const refresh = async (id) => {
    setRefreshing(id);
    setError("");
    setMessage("");

    try {
      await refreshEnvironment(id);

      setMessage(
        "Environmental data refreshed automatically."
      );

      await load();
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Unable to refresh environmental data"
      );
    } finally {
      setRefreshing(null);
    }
  };

  const remove = async (id) => {
    if (
      !window.confirm(
        "Delete this location and its prediction history?"
      )
    ) {
      return;
    }

    try {
      await deleteLocation(id);
      await load();
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Unable to delete location"
      );
    }
  };

  const predict = async (location) => {
    setError("");
    setMessage(
      `Refreshing environmental data and generating prediction for ${location.name}...`
    );

    try {
      await createPrediction(location.id);

      setMessage(
        `Prediction generated for ${location.name}.`
      );

      await load();
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Prediction failed"
      );

      if (err.response?.data?.details) {
        setMessage(err.response.data.details);
      }
    }
  };

  return (
    <div className="app">
      <Sidebar />

      <main className="main">
        <Navbar />

        <div className="content">

          {/* PAGE HEADER */}
          <div className="page-header">
            <div>
              <h1>Flood Monitoring</h1>

              <p>
                Monitor locations and automatically collected
                environmental conditions.
              </p>
            </div>
          </div>

          {message && (
            <div className="success-box">
              {message}
            </div>
          )}

          {error && (
            <div className="error-box">
              {error}
            </div>
          )}

          {/* ADD LOCATION */}
          <div className="location-manager">
            <div className="manager-card">

              <h2>Add a location</h2>

              <p>
                Search for a place and select it. FloodGuard
                automatically fetches elevation, soil moisture,
                terrain slope and available river telemetry.
              </p>

              <div className="search-row">

                <input
                  value={search}
                  onChange={(e) =>
                    setSearch(e.target.value)
                  }
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      findCity();
                    }
                  }}
                  placeholder="Search city, e.g. Darjeeling"
                />

                <button
                  className="primary-button"
                  onClick={findCity}
                >
                  Search
                </button>

              </div>

              {results.length > 0 && (
                <div className="search-results">

                  {results.map((item, index) => (
                    <button
                      key={`${item.name}-${item.latitude}-${index}`}
                      className={
                        selected?.latitude === item.latitude &&
                        selected?.longitude === item.longitude
                          ? "search-result selected"
                          : "search-result"
                      }
                      onClick={() =>
                        setSelected(item)
                      }
                    >
                      <strong>
                        {item.name}
                      </strong>

                      <span>
                        {[item.state, item.country]
                          .filter(Boolean)
                          .join(", ")}
                      </span>
                    </button>
                  ))}

                </div>
              )}

              {selected && (
                <div className="environment-form">

                  <div className="selected-location">
                    <MapPin size={18} />

                    <strong>
                      {selected.name}
                    </strong>

                    <span>
                      {Number(selected.latitude).toFixed(4)},
                      {" "}
                      {Number(selected.longitude).toFixed(4)}
                    </span>
                  </div>

                  <div className="success-box">
                    <strong>
                      Automatic data collection
                    </strong>

                    <br />

                    Elevation · Slope · Soil moisture ·
                    River level

                    <br />

                    No manual environmental input is required.
                  </div>

                  <button
                    className="auth-button"
                    type="button"
                    onClick={add}
                    disabled={loading}
                  >
                    {loading
                      ? "Fetching environmental data..."
                      : "Add Location & Fetch Data"}
                  </button>

                </div>
              )}

            </div>
          </div>

          {/* MAP */}
          <div style={{ marginTop: "20px" }}>
            <FloodMap
              locations={locations}
              predictions={predictions}
            />
          </div>

          {/* LOCATIONS */}
          <div
            className="location-grid"
            style={{ marginTop: "20px" }}
          >

            {locations.map((location) => (
              <div
                className="location-card"
                key={location.id}
              >

                <div className="location-card-header">

                  <div className="location-name">

                    <div className="location-icon">
                      <MapPin size={22} />
                    </div>

                    <div>
                      <h2>
                        {location.name}
                      </h2>

                      <span>
                        {[location.state, location.country]
                          .filter(Boolean)
                          .join(", ")}
                      </span>
                    </div>

                  </div>

                  <button
                    className="icon-btn danger-btn"
                    onClick={() =>
                      remove(location.id)
                    }
                    title="Delete"
                  >
                    <Trash2 size={18} />
                  </button>

                </div>

                <div className="location-stats">

                  <div>
                    <CloudRain size={18} />

                    <span>
                      Soil moisture
                    </span>

                    <strong>
                      {location.soil_moisture ?? "N/A"}%
                    </strong>
                  </div>

                  <div>
                    <Activity size={18} />

                    <span>
                      River level
                    </span>

                    <strong>
                      {location.river_level ?? "N/A"} m
                    </strong>
                  </div>

                </div>

                <div className="location-meta">
                  Slope:{" "}
                  {location.slope ?? "N/A"}°
                  {" · "}
                  Elevation:{" "}
                  {location.elevation ?? "N/A"} m
                </div>

                <div className="location-meta">
                  River station:{" "}
                  {location.river_station_name ||
                    "No available telemetry station"}
                </div>

                <div className="search-row">

                  <button
                    className="location-button"
                    onClick={() =>
                      predict(location)
                    }
                  >
                    Generate Prediction
                  </button>

                  <button
                    className="icon-btn"
                    onClick={() =>
                      refresh(location.id)
                    }
                    disabled={
                      refreshing === location.id
                    }
                    title="Refresh environmental data"
                  >
                    <RefreshCw
                      size={18}
                      className={
                        refreshing === location.id
                          ? "spin"
                          : ""
                      }
                    />
                  </button>

                </div>

              </div>
            ))}

          </div>

          {locations.length === 0 && (
            <div
              className="empty-state"
              style={{ marginTop: "20px" }}
            >
              No locations yet. Add your first
              monitored location above.
            </div>
          )}

        </div>
      </main>
    </div>
  );
}

export default Locations;