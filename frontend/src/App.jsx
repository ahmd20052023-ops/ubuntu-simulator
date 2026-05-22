import React, { useState, useEffect } from "react";
import Terminal from "./components/Terminal";

const API = "/api";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for saved session or create new one
    const saved = localStorage.getItem("ubuntu-sim-session");
    if (saved) {
      fetch(`${API}/sessions/${saved}`)
        .then((r) => {
          if (r.ok) return r.json();
          throw new Error("Session expired");
        })
        .then((data) => {
          setSessionId(data.sessionId);
          setLoading(false);
        })
        .catch(() => createSession());
    } else {
      createSession();
    }
  }, []);

  function createSession() {
    fetch(`${API}/sessions`, { method: "POST" })
      .then((r) => r.json())
      .then((data) => {
        localStorage.setItem("ubuntu-sim-session", data.sessionId);
        setSessionId(data.sessionId);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to create session:", err);
        setLoading(false);
      });
  }

  function handleReset() {
    if (!sessionId) return;
    fetch(`${API}/sessions/${sessionId}/reset`, { method: "POST" })
      .then(() => window.location.reload())
      .catch(console.error);
  }

  if (loading) {
    return (
      <div className="loading">
        <span className="loading-spinner" />
        Starting Ubuntu Simulator...
      </div>
    );
  }

  if (!sessionId) {
    return (
      <div className="loading">
        Failed to connect to server. Make sure the backend is running.
      </div>
    );
  }

  return (
    <div className="window">
      <div className="title-bar">
        <div className="buttons">
          <button className="btn btn-close" onClick={handleReset} title="Reset" />
          <button className="btn btn-minimize" title="Minimize" />
          <button className="btn btn-maximize" title="Maximize" />
        </div>
        <span className="title">user@ubuntu-sim: ~</span>
        <span />
      </div>
      <Terminal sessionId={sessionId} />
    </div>
  );
}
