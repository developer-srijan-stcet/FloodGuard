import { Bell, User } from "lucide-react";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user } = useAuth();

  return (
    <header className="navbar">
      <div>
        <h1>Flood Monitoring</h1>
        <p>Real-time flood risk intelligence</p>
      </div>

      <div className="navbar-actions">
        <button className="icon-btn"><Bell size={20} /></button>
        <div className="profile">
          <div className="profile-icon"><User size={18} /></div>
          <div>
            <strong>{user?.name || "User"}</strong>
            <span>{user?.email || ""}</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
