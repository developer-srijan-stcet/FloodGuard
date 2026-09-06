import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import {
  Activity,
  CloudRain,
  LockKeyhole,
  Mail,
  ShieldCheck,
  ArrowRight,
  Radio,
  Eye,
  EyeOff,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const submit = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      await login(form.email, form.password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(
        err?.response?.data?.error ||
          err?.response?.data?.message ||
          "Invalid email or password"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flood-auth auth-page">
      <div className="auth-layout">

        {/* =====================================================
            LEFT SIDE
        ====================================================== */}

        <section className="auth-visual">

          <div className="auth-image" />
          <div className="auth-image-overlay" />

          {/* Animated particles */}
          <div className="auth-particles" aria-hidden="true">
            <span />
            <span />
            <span />
            <span />
            <span />
            <span />
            <span />
            <span />
          </div>

          <div className="auth-visual-content">

            {/* BRAND */}
            <div className="auth-brand-large">
              <div className="auth-logo-mark">
                <ShieldCheck size={27} />
              </div>

              <div>
                <div className="auth-brand-name">
                  Flood<span>Guard</span>
                </div>

                <div className="auth-brand-subtitle">
                  AI Flood Prediction System
                </div>
              </div>
            </div>

            {/* HERO */}
            <div className="auth-hero-copy">

              <div className="hero-kicker">
                <Radio size={13} />
                REAL-TIME FLOOD INTELLIGENCE
              </div>

              <h1>
                Predict.
                <br />
                <span>Protect.</span>
                <br />
                Prevent.
              </h1>

              <p>
                AI-powered flood prediction using real-time weather,
                environmental and geographical data to help communities
                prepare before danger arrives.
              </p>

            </div>

            {/* FEATURES */}
            <div className="auth-features">

              <div className="auth-feature">
                <div className="feature-icon">
                  <CloudRain size={19} />
                </div>

                <div>
                  <strong>Live Monitoring</strong>
                  <small>Real-time environmental data</small>
                </div>
              </div>

              <div className="auth-feature">
                <div className="feature-icon">
                  <Activity size={19} />
                </div>

                <div>
                  <strong>AI Predictions</strong>
                  <small>Machine-learning risk analysis</small>
                </div>
              </div>

              <div className="auth-feature">
                <div className="feature-icon">
                  <ShieldCheck size={19} />
                </div>

                <div>
                  <strong>Early Warnings</strong>
                  <small>Stay ahead of flood risk</small>
                </div>
              </div>

            </div>
          </div>

          
          {/* WATER EFFECT */}
          <div className="water-wave" />
          <div className="water-wave wave-two" />

        </section>

        {/* =====================================================
            RIGHT SIDE LOGIN
        ====================================================== */}

        <section className="auth-panel">

          <div className="auth-card-modern">

            {/* MOBILE BRAND */}
            <div className="mobile-brand">

              <div className="auth-logo-mark">
                <ShieldCheck size={23} />
              </div>

              <strong>
                Flood<span>Guard</span>
              </strong>

            </div>

            {/* HEADER */}
            <div className="auth-card-header">

              <div className="welcome-badge">
                <span className="online-dot" />
                SECURE ACCESS
              </div>

              <h2>Welcome back</h2>

              <p>
                Sign in to continue monitoring your locations.
              </p>

            </div>

            {/* LOGIN / REGISTER */}
            <div className="auth-tabs">

              <Link
                className="auth-tab active"
                to="/login"
              >
                Login
              </Link>

              <Link
                className="auth-tab"
                to="/register"
              >
                Register
              </Link>

            </div>

            {/* ERROR */}
            {error && (
              <div className="error-box auth-error">
                {error}
              </div>
            )}

            {/* FORM */}
            <form
              onSubmit={submit}
              className="auth-form-modern"
            >

              {/* EMAIL */}
              <div className="modern-field">

                <label htmlFor="login-email">
                  Email address
                </label>

                <div className="field-wrapper">

                  <Mail
                    className="field-icon"
                    size={17}
                  />

                  <input
                    id="login-email"
                    type="email"
                    value={form.email}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        email: e.target.value,
                      })
                    }
                    placeholder="you@example.com"
                    autoComplete="email"
                    required
                  />

                </div>
              </div>

              {/* PASSWORD */}
              <div className="modern-field">

                <label htmlFor="login-password">
                  Password
                </label>

                <div className="field-wrapper">

                  <LockKeyhole
                    className="field-icon"
                    size={17}
                  />

                  <input
                    id="login-password"
                    type={showPassword ? "text" : "password"}
                    value={form.password}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        password: e.target.value,
                      })
                    }
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    required
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() =>
                      setShowPassword(!showPassword)
                    }
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff size={17} />
                    ) : (
                      <Eye size={17} />
                    )}
                  </button>

                </div>
              </div>

              {/* OPTIONS */}
              <div className="auth-options">

                <label className="remember">

                  <input type="checkbox" />

                  <span>
                    Remember me
                  </span>

                </label>

                <button
                  type="button"
                  className="forgot-password"
                >
                  Forgot password?
                </button>

              </div>

              {/* BUTTON */}
              <button
                className="auth-button-modern"
                disabled={loading}
                type="submit"
              >

                <span>
                  {loading
                    ? "Signing in..."
                    : "Sign in"}
                </span>

                {!loading && (
                  <ArrowRight
                    className="button-arrow"
                    size={19}
                  />
                )}

              </button>

            </form>

            {/* FOOTER */}
            <p className="auth-footer-modern">

              <span>
                Don't have an account?
              </span>

              <Link to="/register">
                Create account
              </Link>

            </p>

            <div className="security-note">
              <ShieldCheck size={13} />
              <span>
                Your data is protected with secure authentication.
              </span>
            </div>

          </div>
        </section>
      </div>
    </div>
  );
}

export default Login;