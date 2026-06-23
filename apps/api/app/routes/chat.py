"""Endpoint POST /chat — przyjmuje wiadomość i zwraca odpowiedź bota."""
from flask import Blueprint, jsonify, request

from ..claude import get_reply

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []

    # Walidacja wejścia.
    if not message:
        return jsonify({"error": "Pole 'message' jest wymagane."}), 400
    if not isinstance(history, list):
        return jsonify({"error": "Pole 'history' musi być listą."}), 400

    # Wywołanie modelu + obsługa błędów (np. brak klucza API).
    try:
        reply = get_reply(message, history)
        return jsonify({"reply": reply})
    except Exception as exc:  # noqa: BLE001 - świadomie łapiemy wszystko
        return jsonify({"error": str(exc)}), 500
