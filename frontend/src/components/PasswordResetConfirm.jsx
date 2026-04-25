import React, { useState } from "react";
import axios from "axios";
import { moviesAPI } from "../services/api";
const API_BASE_URL = moviesAPI ? moviesAPI.constructor?.API_BASE_URL || moviesAPI.API_BASE_URL || (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');

function PasswordResetConfirm({ token }) {
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");
    try {
      const res = await axios.post(`${API_BASE_URL}/api/auth/password-reset/${token}/`, { new_password: newPassword });
      setMessage(res.data.message);
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong");
    }
  };

  return (
    <div className="password-reset-confirm">
      <h2>Set New Password</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="password"
          placeholder="New password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />
        <button type="submit">Reset Password</button>
      </form>
      {message && <div style={{ color: "green" }}>{message}</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
    </div>
  );
}

export default PasswordResetConfirm;
