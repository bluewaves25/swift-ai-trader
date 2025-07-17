import React, { useEffect, useState } from "react";

const API_URL = "/api/engine/status";

export const EngineStatus: React.FC = () => {
  const [status, setStatus] = useState<string | null>(null);
  const [lastHeartbeat, setLastHeartbeat] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      setStatus(data.status);
      setLastHeartbeat(data.last_heartbeat);
    } catch (e) {
      setStatus("error");
      setLastHeartbeat(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  let color = "gray";
  if (status === "running") color = "green";
  if (status === "not running") color = "red";
  if (status === "error") color = "orange";

  return (
    <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 16, maxWidth: 350 }}>
      <h3>Engine Status</h3>
      {loading ? (
        <span>Loading...</span>
      ) : (
        <>
          <span style={{ color, fontWeight: "bold" }}>
            {status === "running" && "🟢 Running"}
            {status === "not running" && "🔴 Not Running"}
            {status === "error" && "⚠️ Error"}
          </span>
          <br />
          <small>Last heartbeat: {lastHeartbeat ? new Date(lastHeartbeat).toLocaleString() : "-"}</small>
        </>
      )}
    </div>
  );
};

export default EngineStatus; 