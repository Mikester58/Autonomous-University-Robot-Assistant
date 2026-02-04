import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../services/authService";
import "../styles/login.css";
import logo from "../assets/robot.png";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("student@tamu.edu");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(email.trim() || "student@tamu.edu");
    navigate("/", { replace: true }); // ✅ force route change
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <img src={logo} alt="ARUA" className="login-logo" />
          <div className="login-brand-text">
            <h1 className="login-title">ARUA</h1>
            <p className="login-subtitle">Control Panel Access</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <label className="login-label" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            className="login-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="student@tamu.edu"
            autoComplete="email"
          />

          <button className="login-btn" type="submit">
            Login
          </button>

          <div className="login-footnote">Local dev auth (temporary)</div>
        </form>
      </div>
    </div>
  );
}
