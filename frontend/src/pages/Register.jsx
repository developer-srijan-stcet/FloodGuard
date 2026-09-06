import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const submit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await register(form);

      setSuccess("Registration successful. Redirecting to login...");

      setTimeout(() => {
        navigate("/login");
      }, 800);
    } catch (err) {
      setError(
        err?.response?.data?.error ||
        err?.message ||
        "Registration failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page flood-auth">

      {/* Animated particles */}
      <div className="auth-particles">
        <span></span>
        <span></span>
        <span></span>
        <span></span>
        <span></span>
        <span></span>
      </div>

      <div className="auth-layout">

        {/* ================= LEFT SIDE ================= */}
        <section className="auth-visual">

          <div className="auth-image"></div>
          <div className="auth-image-overlay"></div>

          <div className="auth-visual-content">

            {/* BRAND */}
            <div className="auth-brand-large">

              <div className="auth-logo-mark">
                🌊
              </div>

              <div>
                <div className="auth-brand-name">
                  Flood<span>Guard</span>
                </div>

                <div className="auth-brand-subtitle">
                  Prediction System
                </div>
              </div>

            </div>


            {/* HERO */}
            <div className="auth-hero-copy">

              <div className="hero-kicker">
                FLOOD INTELLIGENCE PLATFORM
              </div>

              <h1>
                Stay
                <br />
                <span>Prepared.</span>
              </h1>

              <p>
                Create your FloodGuard account and start
                monitoring flood risk with intelligent,
                real-time environmental data.
              </p>

            </div>


            {/* FEATURES */}
            <div className="auth-features">

              <div className="auth-feature">

                <div className="feature-icon">
                  📍
                </div>

                <div>
                  <strong>Monitor Locations</strong>
                  <small>
                    Track important areas
                  </small>
                </div>

              </div>


              <div className="auth-feature">

                <div className="feature-icon">
                  🌦️
                </div>

                <div>
                  <strong>Weather Intelligence</strong>
                  <small>
                    Live environmental conditions
                  </small>
                </div>

              </div>


              <div className="auth-feature">

                <div className="feature-icon">
                  🚨
                </div>

                <div>
                  <strong>Flood Alerts</strong>
                  <small>
                    Receive early warnings
                  </small>
                </div>

              </div>

            </div>


            

          </div>


          <div className="water-wave wave-one"></div>
          <div className="water-wave wave-two"></div>

        </section>


        {/* ================= RIGHT SIDE ================= */}
        <section className="auth-panel">

          <div className="auth-card-modern">

            {/* MOBILE BRAND */}
            <div className="mobile-brand">

              <div className="auth-logo-mark">
                🌊
              </div>

              <div>

                <div className="auth-brand-name">
                  Flood<span>Guard</span>
                </div>

                <div className="auth-brand-subtitle">
                  Prediction System
                </div>

              </div>

            </div>


            {/* HEADER */}
            <div className="auth-card-header">

              <div className="welcome-badge">
                <span className="online-dot"></span>
                System online
              </div>

              <h2>
                Create account
              </h2>

              <p>
                Register to start monitoring flood risk.
              </p>

            </div>


            {/* LOGIN / REGISTER TABS */}
            <div className="auth-tabs">

              <Link
                to="/login"
                className="auth-tab"
              >
                Login
              </Link>

              <div className="auth-tab active">
                Register
              </div>

            </div>


            {/* ERROR */}
            {error && (
              <div className="auth-error">
                <span>⚠</span>
                {error}
              </div>
            )}


            {/* SUCCESS */}
            {success && (
              <div className="auth-success">
                <span>✓</span>
                {success}
              </div>
            )}


            {/* FORM */}
            <form
              className="auth-form-modern"
              onSubmit={submit}
            >

              {/* NAME */}
              <div className="modern-field">

                <label>
                  Full Name
                </label>

                <div className="field-wrapper">

                  <span className="field-icon">
                    👤
                  </span>

                  <input
                    type="text"
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    placeholder="Your name"
                    required
                  />

                </div>

              </div>


              {/* EMAIL */}
              <div className="modern-field">

                <label>
                  Email address
                </label>

                <div className="field-wrapper">

                  <span className="field-icon">
                    ✉
                  </span>

                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="you@example.com"
                    required
                  />

                </div>

              </div>


              {/* PHONE */}
              <div className="modern-field">

                <label>
                  WhatsApp Number
                </label>

                <div className="field-wrapper">

                  <span className="field-icon">
                    📱
                  </span>

                  <input
                    type="tel"
                    name="phone"
                    value={form.phone}
                    onChange={handleChange}
                    placeholder="+91XXXXXXXXXX"
                    required
                  />

                </div>

              </div>


              {/* PASSWORD */}
              <div className="modern-field">

                <label>
                  Password
                </label>

                <div className="field-wrapper">

                  <span className="field-icon">
                    🔒
                  </span>

                  <input
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="Minimum 6 characters"
                    minLength={6}
                    required
                  />

                </div>

              </div>


              {/* BUTTON */}
              <button
                type="submit"
                className="auth-button-modern"
                disabled={loading}
              >

                <span>
                  {loading
                    ? "Creating account..."
                    : "Create account"}
                </span>

                {!loading && (
                  <span className="button-arrow">
                    →
                  </span>
                )}

              </button>

            </form>


            {/* FOOTER */}
            <div className="auth-footer-modern">

              Already have an account?

              <Link to="/login">
                Sign in
              </Link>

            </div>


            <div className="security-note">
              <span>🛡️</span>
              Your data is protected with secure authentication.
            </div>

          </div>

        </section>

      </div>

    </div>
  );
}