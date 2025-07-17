import React, { useState } from "react";

const EngineFeed: React.FC = () => {
  const [symbol, setSymbol] = useState("");
  const [price, setPrice] = useState("");
  const [volume, setVolume] = useState("");
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendFeed = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const payload = [{
        timestamp: new Date().toISOString(),
        symbol,
        open: parseFloat(price),
        high: parseFloat(price),
        low: parseFloat(price),
        close: parseFloat(price),
        volume: parseFloat(volume)
      }];
      const res = await fetch("/api/engine/feed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      setResponse(JSON.stringify(data));
    } catch (e) {
      setError("Failed to send feed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 16, maxWidth: 350, marginTop: 16 }}>
      <h3>Engine Feed (Manual)</h3>
      <input value={symbol} onChange={e => setSymbol(e.target.value)} placeholder="Symbol" style={{ width: "100%", marginBottom: 8 }} />
      <input value={price} onChange={e => setPrice(e.target.value)} placeholder="Price" type="number" style={{ width: "100%", marginBottom: 8 }} />
      <input value={volume} onChange={e => setVolume(e.target.value)} placeholder="Volume" type="number" style={{ width: "100%", marginBottom: 8 }} />
      <button onClick={sendFeed} disabled={loading || !symbol || !price || !volume} style={{ marginRight: 8 }}>
        {loading ? "Sending..." : "Send"}
      </button>
      {response && <div style={{ marginTop: 12, color: "#333" }}>Response: {response}</div>}
      {error && <div style={{ marginTop: 12, color: "red" }}>{error}</div>}
    </div>
  );
};

export default EngineFeed; 