"use client";

import { useEffect, useRef, useState } from "react";

type Role = "user" | "bot";

interface Message {
  role: Role;
  text: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5001";

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", text: "Cześć! Zapytaj mnie o dorobek naukowy SWPS." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    // Prior turns become conversation history (bot -> assistant for the API).
    const history = messages.map((m) => ({
      role: m.role === "user" ? "user" : "assistant",
      content: m.text,
    }));

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setError(null);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.error ?? `Żądanie nie powiodło się (${res.status})`);
      }

      setMessages((prev) => [...prev, { role: "bot", text: data.reply }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Coś poszło nie tak");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card shadow-sm" style={{ width: "100%", maxWidth: 640 }}>
      <div className="card-header bg-primary text-white d-flex align-items-center gap-2">
        <span
          className="rounded-circle bg-success d-inline-block"
          style={{ width: 10, height: 10 }}
          aria-hidden
        />
        <strong>Chatbot</strong>
      </div>

      <div
        ref={scrollRef}
        className="card-body d-flex flex-column gap-2 overflow-auto"
        style={{ height: 420 }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            className={`d-flex ${
              m.role === "user" ? "justify-content-end" : "justify-content-start"
            }`}
          >
            <div
              className={`px-3 py-2 rounded-3 ${
                m.role === "user"
                  ? "bg-primary text-white"
                  : "bg-light border text-dark"
              }`}
              style={{ maxWidth: "75%", whiteSpace: "pre-wrap" }}
            >
              {m.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="d-flex justify-content-start">
            <div className="px-3 py-2 rounded-3 bg-light border text-muted">
              <span
                className="spinner-grow spinner-grow-sm me-1"
                role="status"
                aria-hidden
              />
              pisze…
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="alert alert-danger m-3 mb-0 py-2" role="alert">
          {error}
        </div>
      )}

      <form className="card-footer" onSubmit={sendMessage}>
        <div className="input-group">
          <input
            type="text"
            className="form-control"
            placeholder="Napisz wiadomość…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            aria-label="Wiadomość"
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !input.trim()}
          >
            Wyślij
          </button>
        </div>
      </form>
    </div>
  );
}
