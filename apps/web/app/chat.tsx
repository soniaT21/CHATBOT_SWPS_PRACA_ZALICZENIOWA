"use client";

import { useEffect, useRef, useState } from "react";

type Message = { role: "user" | "assistant"; content: string };

// Adres backendu. Można nadpisać w apps/web/.env.local (NEXT_PUBLIC_API_URL).
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

const POWITANIE: Message = {
  role: "assistant",
  content:
    "Cześć! Jestem Asystentem SWPS. Zapytaj mnie np. o publikację SWPS " +
    "o psychologii pozytywnej.",
};

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([POWITANIE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  // Automatyczne przewijanie na dół przy nowej wiadomości.
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;

    // Historia BEZ powitania (indeks 0) i bez aktualnej wiadomości —
    // tę wysyłamy osobno jako "message". Dzięki temu role poprawnie
    // przeplatają się po stronie backendu.
    const history = messages
      .slice(1)
      .map((m) => ({ role: m.role, content: m.content }));

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history }),
      });
      const data = await res.json();
      const reply =
        data.reply ||
        data.error ||
        "Przepraszam, coś poszło nie tak.";
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Nie mogę połączyć się z serwerem. Sprawdź, czy backend działa " +
            "(yarn dev) na " + API_URL + ".",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    // Enter wysyła, Shift+Enter robi nową linię.
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="card shadow-sm">
      {/* Okno z wiadomościami */}
      <div
        className="card-body overflow-auto"
        style={{ height: "60vh", minHeight: 320 }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            className={`d-flex mb-3 ${
              m.role === "user" ? "justify-content-end" : "justify-content-start"
            }`}
          >
            <div
              className={`chat-bubble px-3 py-2 rounded-3 ${
                m.role === "user"
                  ? "bg-primary text-white"
                  : "bg-light border"
              }`}
              style={{ maxWidth: "80%" }}
            >
              {m.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="d-flex mb-3 justify-content-start">
            <div className="chat-bubble px-3 py-2 rounded-3 bg-light border">
              <span className="typing-dot">●</span>{" "}
              <span className="typing-dot">●</span>{" "}
              <span className="typing-dot">●</span>
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {/* Pole wpisywania */}
      <div className="card-footer bg-white">
        <div className="input-group">
          <textarea
            className="form-control"
            rows={1}
            placeholder="Napisz wiadomość..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={loading}
          />
          <button
            className="btn btn-primary"
            type="button"
            onClick={send}
            disabled={loading || !input.trim()}
          >
            Wyślij
          </button>
        </div>
      </div>
    </div>
  );
}
