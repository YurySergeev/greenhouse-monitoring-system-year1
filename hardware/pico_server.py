from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import certifi
import os
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# App + DB init
# --------------------------------------------------

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "").strip()
DB_NAME   = os.getenv("DB_NAME", "greenhouse_db").strip()

try:
    client     = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db         = client[DB_NAME]
    collection = db["sensor_readings"]
    # Ping to confirm connection on startup
    client.admin.command("ping")
    print(f"[DB] Connected to MongoDB — '{DB_NAME}'")
except Exception as e:
    print(f"[DB] Connection failed: {e}")
    client     = None
    db         = None
    collection = None


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.route("/ping", methods=["GET"])
def ping():
    """Health-check — lets you confirm the server is reachable."""
    return jsonify({"status": "ok", "message": "Server is running"}), 200


@app.route("/data", methods=["POST"])
def receive_data():
    """
    Accepts a JSON POST from the Pico W and saves it to MongoDB.

    Expected payload from Pico:
    {
        "node_id":        "pico_prototype_1",
        "temperature_c":  23.4,
        "humidity_rh":    58.0
    }
    """
    # ── 1. Parse incoming JSON ──────────────────────────────────────────────
    incoming = request.get_json(silent=True)

    if not incoming:
        return jsonify({"status": "error", "message": "No JSON received"}), 400

    print(f"[POST /data] Received: {incoming}")

    # ── 2. Validate required fields ─────────────────────────────────────────
    required = ["node_id", "temperature_c", "humidity_rh"]
    missing  = [f for f in required if f not in incoming]

    if missing:
        return jsonify({
            "status":  "error",
            "message": f"Missing fields: {missing}"
        }), 400

    # ── 3. Build the document ───────────────────────────────────────────────
    record = {
        "node_id":       incoming["node_id"],
        "zone":          incoming.get("zone", "zone1"),
        "area":          incoming.get("area", "upper_plants"),
        "source":        "pico_w",
        "temperature_c": float(incoming["temperature_c"]),
        "humidity_rh":   float(incoming["humidity_rh"]),
        "ts":            datetime.utcnow(),
    }

    # ── 4. Insert into MongoDB ──────────────────────────────────────────────
    if collection is None:
        print("[DB] No DB connection — data not saved.")
        return jsonify({
            "status":  "error",
            "message": "Database unavailable"
        }), 503

    try:
        result = collection.insert_one(record)
        print(f"[DB] Inserted document id: {result.inserted_id}")
    except Exception as e:
        print(f"[DB] Insert failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

    # ── 5. Respond to Pico ──────────────────────────────────────────────────
    return jsonify({
        "status":  "success",
        "message": "Data saved",
        "id":      str(result.inserted_id)
    }), 200


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    # host='0.0.0.0' lets devices on the same Wi-Fi reach this server.
    # Change port if 5000 is taken.
    print("[Server] Starting on 0.0.0.0:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=False)