import React, { useState } from "react";

interface SupportChatModalProps {
  open: boolean;
  onClose: () => void;
}

const SupportChatModal: React.FC<SupportChatModalProps> = ({ open, onClose }) => {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const res = await fetch("/api/support/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      setResponse(data.response);
    } catch (e) {
      setError("Failed to send message");
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.3)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
      <div style={{ background: "#fff", borderRadius: 8, padding: 24, minWidth: 320, maxWidth: 400 }}>
        <h3>Support Chat</h3>
        <textarea
          value={message}
          onChange={e => setMessage(e.target.value)}
          rows={3}
          style={{ width: "100%", marginBottom: 8 }}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage} disabled={loading || !message.trim()} style={{ marginRight: 8 }}>
          {loading ? "Sending..." : "Send"}
        </button>
        <button onClick={onClose}>Close</button>
        {response && <div style={{ marginTop: 12, color: "#333" }}>Support: {response}</div>}
        {error && <div style={{ marginTop: 12, color: "red" }}>{error}</div>}
      </div>
    </div>
  );
};

export default SupportChatModal; 