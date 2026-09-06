import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

import Dashboard from "./pages/Dashboard";
import Locations from "./pages/Locations";
import Weather from "./pages/Weather";
import Predictions from "./pages/Predictions";
import Alerts from "./pages/Alerts";
import Login from "./pages/Login";
import Register from "./pages/Register";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return <div className="loading-screen">Loading...</div>;
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/"
        element={<ProtectedRoute><Dashboard /></ProtectedRoute>}
      />
      <Route
        path="/locations"
        element={<ProtectedRoute><Locations /></ProtectedRoute>}
      />
      <Route
        path="/weather"
        element={<ProtectedRoute><Weather /></ProtectedRoute>}
      />
      <Route
        path="/predictions"
        element={<ProtectedRoute><Predictions /></ProtectedRoute>}
      />
      <Route
        path="/alerts"
        element={<ProtectedRoute><Alerts /></ProtectedRoute>}
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
