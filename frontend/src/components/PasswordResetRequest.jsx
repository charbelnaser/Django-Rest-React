import React, { useState } from "react";
import axios from "axios";
import { moviesAPI } from "../services/api";
const API_BASE_URL = moviesAPI ? moviesAPI.constructor?.API_BASE_URL || moviesAPI.API_BASE_URL || (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');

function PasswordResetRequest() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");
    try {
      const res = await axios.post(`${API_BASE_URL}/api/auth/password-reset/`, { email });
      setMessage(res.data.message);
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong");
    }
  };

  return (
    <div className="password-reset-request">
      <h2>Reset Password</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <button type="submit">Send Reset Link</button>
      </form>
      {message && <div style={{ color: "green" }}>{message}</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
    </div>
  );
}

export default PasswordResetRequest;
