import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";

function riskColor(risk) {
  if (risk >= 80) return "#991b1b";
  if (risk >= 60) return "#dc2626";
  if (risk >= 40) return "#d97706";
  if (risk >= 20) return "#16a34a";
  return "#2563eb";
}

function MapViewport({ points }) {
  const map = useMap();

  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();

      if (points.length === 0) {
        map.setView([22.5726, 88.3639], 7, {
          animate: false,
        });
        return;
      }

      if (points.length === 1) {
        map.flyTo(
          [
            Number(points[0].latitude),
            Number(points[0].longitude),
          ],
          10,
          {
            animate: true,
            duration: 0.8,
          }
        );
        return;
      }

      const bounds = points.map((point) => [
        Number(point.latitude),
        Number(point.longitude),
      ]);

      map.fitBounds(bounds, {
        padding: [50, 50],
        maxZoom: 10,
        animate: true,
        duration: 0.8,
      });
    }, 150);

    return () => clearTimeout(timer);
  }, [map, points]);

  return null;
}

function FloodMap({
  locations = [],
  predictions = [],
}) {
  const points = locations
    .map((location) => {
      const latitude = Number(location.latitude);
      const longitude = Number(location.longitude);

      if (
        !Number.isFinite(latitude) ||
        !Number.isFinite(longitude)
      ) {
        return null;
      }

      const prediction = predictions.find(
        (p) =>
          Number(p.location_id) === Number(location.id)
      );

      return {
        ...location,
        latitude,
        longitude,
        risk:
          prediction?.flood_probability != null
            ? Number(prediction.flood_probability)
            : null,
        riskLevel:
          prediction?.risk_level || "NO DATA",
      };
    })
    .filter(Boolean);

  const center =
    points.length > 0
      ? [points[0].latitude, points[0].longitude]
      : [22.5726, 88.3639];

  return (
    <div className="flood-map-shell">
      <div className="map-live-badge">
        <span />
        Live monitored locations
      </div>

      <MapContainer
        center={center}
        zoom={7}
        minZoom={3}
        maxZoom={18}
        scrollWheelZoom={true}
        doubleClickZoom={true}
        zoomControl={true}
        zoomAnimation={true}
        fadeAnimation={true}
        markerZoomAnimation={true}
        preferCanvas={false}
        wheelPxPerZoomLevel={80}
        zoomDelta={0.5}
        zoomSnap={0.5}
        className="leaflet-flood-map"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
          keepBuffer={4}
        />

        <MapViewport points={points} />

        {points.map((location) => {
          const color =
            location.risk == null
              ? "#64748b"
              : riskColor(location.risk);

          return (
            <CircleMarker
              key={location.id}
              center={[
                location.latitude,
                location.longitude,
              ]}
              radius={11}
              pathOptions={{
                color: "#ffffff",
                fillColor: color,
                fillOpacity: 1,
                weight: 3,
              }}
            >
              <Popup>
                <div className="map-popup">
                  <strong>{location.name}</strong>

                  <span>
                    {location.state ||
                      location.country ||
                      "Monitored location"}
                  </span>

                  <div>
                    <b>Flood probability:</b>{" "}
                    {location.risk == null
                      ? "No prediction"
                      : `${location.risk.toFixed(1)}%`}
                  </div>

                  <div>
                    <b>Risk level:</b>{" "}
                    {location.riskLevel}
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}

export default FloodMap;