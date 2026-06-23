"""Fabryka aplikacji Flask.

Tworzy instancję aplikacji, włącza CORS (żeby frontend z portu 3000
mógł wołać API z portu 5001) i rejestruje endpointy (/chat, /health).
"""
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# Wczytujemy zmienne z pliku .env (klucz API, RAG_ENABLED itd.)
load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    # Pozwalamy przeglądarce wołać API z innego portu (frontend: 3000).
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Rejestrujemy trasy (blueprinty).
    from .routes.chat import chat_bp
    from .routes.health import health_bp

    app.register_blueprint(chat_bp)
    app.register_blueprint(health_bp)

    return app
