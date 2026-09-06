function RiskCard({ probability = 72 }) {

  let level = "HIGH";

  if (probability < 20) level = "SAFE";
  else if (probability < 40) level = "LOW";
  else if (probability < 60) level = "MODERATE";
  else if (probability < 80) level = "HIGH";
  else level = "EXTREME";

  return (
    <div className="risk-card">

      <div className="risk-header">
        <div>
          <p>Current Flood Risk</p>
          <h2>{level}</h2>
        </div>

        <div className="risk-percentage">
          {probability}%
        </div>
      </div>

      <div className="progress">

        <div
          className="progress-bar"
          style={{ width: `${probability}%` }}
        />

      </div>

      <p className="risk-info">
        AI prediction based on rainfall, humidity,
        soil conditions and historical flood data.
      </p>

    </div>
  );
}

export default RiskCard;