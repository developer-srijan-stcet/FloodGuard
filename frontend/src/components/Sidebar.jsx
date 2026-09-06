import { NavLink } from "react-router-dom";
import { Activity, CloudRain, LayoutDashboard, LogOut, Map, TriangleAlert } from "lucide-react";
import { useAuth } from "../context/AuthContext";

function Sidebar() {
  const { logout } = useAuth();

  const menu = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Locations", path: "/locations", icon: Map },
    { name: "Predictions", path: "/predictions", icon: Activity },
    { name: "Weather", path: "/weather", icon: CloudRain },
    { name: "Alerts", path: "/alerts", icon: TriangleAlert }
  ];

  return (
    <aside className="sidebar">
      <div className="logo">
        <div className="logo-icon">🌊</div>
        <div>
          <h2>FloodGuard</h2>
          <span>Prediction System</span>
        </div>
      </div>

      <nav>
        {menu.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}
            >
              <Icon size={20} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <button className="logout-btn" onClick={logout}>
          <LogOut size={18} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
