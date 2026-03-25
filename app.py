import os, json, urllib.request, urllib.parse, datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from scanner import run_scan_all, get_alert_status

app = Flask(__name__)
CORS(app, supports_credentials=True, origins="*")

# ====== Upstox Token Management ======
_token = {"value": os.environ.get("UPSTOX_TOKEN", "")}
def get_token(): return _token["value"]
def set_token(tok): _token["value"] = tok.strip()

@app.route("/ping")
def ping():
    return jsonify({"status":"ok","token_set":bool(get_token())})

@app.route("/get-token")
def get_tok():
    return jsonify({"token": get_token()})

@app.route("/set-token", methods=["POST"])
def set_tok():
    data = request.get_json()
    tok = data.get("token")
    if not tok: return jsonify({"error":"No token"}),400
    set_token(tok)
    return jsonify({"status":"ok"})

# ====== Proxy Routes ======
UPSTOX_BASE="https://api.upstox.com"
def upstox_request(path, ikey, qs=""):
    url = f"{UPSTOX_BASE}{path}?instrument_key={urllib.parse.quote(ikey,safe='')}"
    if qs: url += "&"+qs
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {get_token()}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

@app.route("/upstox/ltp")
def proxy_ltp():
    ikey = request.args.get("ikey")
    return jsonify(upstox_request("/v2/market-quote/ltp", ikey))

@app.route("/upstox/intraday")
def proxy_intraday():
    ikey = request.args.get("ikey")
    interval = request.args.get("interval","1minute")
    return jsonify(upstox_request("/v2/instruments/candles", ikey, f"interval={interval}"))

@app.route("/upstox/daily")
def proxy_daily():
    ikey = request.args.get("ikey")
    from_d = request.args.get("from")
    to_d = request.args.get("to")
    return jsonify(upstox_request("/v2/instruments/candles", ikey, f"from={from_d}&to={to_d}&interval=1day"))

# ====== Macro + Scanner ======
@app.route("/scan")
def scan():
    data = run_scan_all()
    return jsonify(data)

@app.route("/alert-status")
def alert_status():
    return jsonify(get_alert_status())

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)