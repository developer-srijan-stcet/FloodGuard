import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api",
  headers: {
    "Content-Type": "application/json"
  }
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.dispatchEvent(new Event("auth-expired"));
    }
    return Promise.reject(error);
  }
);

export const login = (data) => API.post("/auth/login", data);
export const register = (data) => API.post("/auth/register", data);
export const getMe = () => API.get("/auth/me");

export const searchLocations = (city) =>
  API.get("/location/search", { params: { city } });

export const getLocations = () => API.get("/locations");
export const createLocation = (data) => API.post("/locations", data);
export const deleteLocation = (id) => API.delete(`/locations/${id}`);
export const refreshEnvironment = (id) => API.post(`/locations/${id}/refresh-environment`);

export const getWeather = (latitude, longitude) =>
  API.get("/weather", {
    params: { lat: latitude, lon: longitude }
  });

export const createPrediction = (locationId) =>
  API.post("/predict", { location_id: locationId });

export const getPredictions = () => API.get("/predict/history");

export const getAlerts = () => API.get("/alerts");
export const sendAlert = (predictionId) =>
  API.post(`/alerts/send/${predictionId}`);

export default API;
