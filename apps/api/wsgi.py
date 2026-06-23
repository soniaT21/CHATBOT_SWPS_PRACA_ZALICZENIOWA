"""Punkt wejścia backendu.

Uruchamia serwer deweloperski Flask. Port bierzemy z .env (domyślnie 5001),
żeby zgadzał się z frontendem (apps/web/app/chat.tsx).
"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=True)
