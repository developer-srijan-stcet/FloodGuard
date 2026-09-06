import { TriangleAlert } from "lucide-react";

function AlertCard({ title, message, time }) {

  return (
    <div className="alert-card">

      <div className="alert-icon">
        <TriangleAlert size={22} />
      </div>

      <div>

        <h3>{title}</h3>

        <p>{message}</p>

        <span>{time}</span>

      </div>

    </div>
  );
}

export default AlertCard;