import { useEffect, useState } from "react";
import { API_ENDPOINTS, apiCall } from "@/config/api";

interface EngineStatusData {
  performance_metrics?: Record<string, unknown>;
  current_regime?: string;
  volatility_level?: number;
  strategies?: string[];
  sandbox_strategies?: string[];
  explain_log?: unknown[];
}

export default function EngineStatus() {
  const [status, setStatus] = useState<EngineStatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    apiCall(API_ENDPOINTS.ENGINE_STATUS)
      .then((res: EngineStatusData) => {
        setStatus(res);
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to fetch engine status");
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading engine status...</div>;
  if (error) return <div>{error}</div>;
  if (!status) return <div>No engine status available.</div>;

  return (
    <div>
      <h2>Engine Diagnostics</h2>
      <pre style={{ background: "#f5f5f5", padding: 12, borderRadius: 6 }}>
        {JSON.stringify(status.performance_metrics || {}, null, 2)}
      </pre>
      <div>Current Regime: <b>{status.current_regime || "-"}</b></div>
      <div>Volatility Level: <b>{status.volatility_level ?? "-"}</b></div>
      <div>Active Strategies: <b>{Array.isArray(status.strategies) ? status.strategies.join(", ") : "-"}</b></div>
      <div>Sandbox Strategies: <b>{Array.isArray(status.sandbox_strategies) ? status.sandbox_strategies.join(", ") : "-"}</b></div>
      <h3>Explainability Log (last 10 events)</h3>
      <ul>
        {(status.explain_log || []).map((log: any, idx: number) => (
          <li key={idx}>
            <pre style={{ background: "#eee", padding: 8, borderRadius: 4 }}>{JSON.stringify(log, null, 2)}</pre>
          </li>
        ))}
      </ul>
    </div>
  );
} 