import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import yfinance as yf
import pandas as pd
import threading
import time
import json
from flask_sockets import Sockets  # WebSocket support

# --- Flask App ---
app = Flask(__name__)
CORS(app)
sockets = Sockets(app)

# --- Environment Variables ---
UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- In-Memory Data Store ---
market_data = {}
ws_clients = set()
lock = threading.Lock()

# --- Health Route ---
@app.route("/")
def health():
    return jsonify({"status": "up"})

# --- REST Endpoint for LTP ---
@app.route("/v2/market-quote/ltp")
def ltp():
    instrument_key = request.args.get("instrument_key")
    if not instrument_key:
        return jsonify({"error": "instrument_key required"}), 400

    # Example: Using yfinance for simplicity
    try:
        ticker = instrument_key.replace("|", "-")  # NIFTY 50 → NIFTY-50
        data = yf.Ticker(ticker).history(period="1d", interval="1m")
        if data.empty:
            return jsonify({"error": "no data"}), 404
        last_row = data.tail(1).to_dict(orient="records")[0]
        return jsonify(last_row)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- WebSocket for real-time updates ---
@sockets.route("/ws/market")
def market_socket(ws):
    ws_clients.add(ws)
    try:
        while not ws.closed:
            with lock:
                # Broadcast latest data to all connected clients
                for ticker, quote in market_data.items():
                    ws.send(json.dumps({ticker: quote}))
            time.sleep(1)  # Auto refresh every 1 sec
    finally:
        ws_clients.remove(ws)

# --- Background Updater ---
def fetch_market_data():
    tickers = ["NSE-INDEX-NIFTY50", "NSE-INDEX-SENSEX"]  # Add more tickers
    for t in tickers:
        try:
            data = yf.Ticker(t).history(period="1d", interval="1m")
            if not data.empty:
                last_row = data.tail(1).to_dict(orient="records")[0]
                with lock:
                    market_data[t] = last_row
        except Exception:
            continue

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_market_data, "interval", seconds=10)
scheduler.start()

# --- Main Entry ---
if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    print("Starting Flask + WebSocket server...")
    server = pywsgi.WSGIServer(
        ("0.0.0.0", int(os.getenv("PORT", 5000))),
        app,
        handler_class=WebSocketHandler,
    )
    server.serve_forever()
