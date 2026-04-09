from flask import Flask, jsonify, request
from db import get_all_data, get_zone_data, get_latest, get_history, get_readings
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone

from pymongo import MongoClient
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "greenhouse_db")

client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = client[DB_NAME]

app = Flask(__name__)

@app.route("/data")
def data():
    return jsonify(get_all_data())

@app.route("/zone/<zone_name>")
def zone(zone_name):
    return jsonify(get_zone_data(zone_name))

@app.route("/latest")
def latest():
    zone = request.args.get("zone")
    area = request.args.get("area")
    source = request.args.get("source")
    result = get_latest(zone=zone, area=area, source=source)
    return jsonify(result)

@app.route("/history")
def history():
    zone = request.args.get("zone")
    area = request.args.get("area")
    source = request.args.get("source")
    result = get_history(zone=zone, area=area, source=source)
    return jsonify(result)

@app.route("/readings")
def readings():
    zone = request.args.get("zone")
    area = request.args.get("area")
    source = request.args.get("source")
    limit = int(request.args.get("limit", 20))
    result = get_readings(zone=zone, area=area, source=source, limit=limit)
    return jsonify(result)

# endpoints to retrieve sensor data

@app.route("/api/sensor/latest", methods=["GET"])
def get_latest_sensor():
    zone = request.args.get("zone", "zone1")
    area = request.args.get("area", "upper_plants")

    doc = db.zone1_dht22_test.find_one(
        {"zone": zone, "area": area, "source": "pico_w"},
        sort=[("ts", -1)]
    )

    if doc:
        doc["_id"] = str(doc["_id"])
        doc["ts"] = doc["ts"].isoformat()
        return jsonify(doc)

    return jsonify(None)

@app.route("/api/sensor/history", methods=["GET"])
def get_sensor_history():
    zone = request.args.get("zone", "zone1")
    area = request.args.get("area", "upper_plants")

    hours = request.args.get("hours", type=int)
    start_ts = request.args.get("start_ts")
    end_ts = request.args.get("end_ts")

    if start_ts and end_ts:
        ts_query = {
            "$gte": datetime.fromisoformat(start_ts),
            "$lte": datetime.fromisoformat(end_ts)
        }
    else:
        # be weary of this usage of datetime.utcnow(), deprecated but things are working still 
        since = datetime.utcnow() - timedelta(hours=hours or 24)
        ts_query = {"$gte": since}

    docs = list(db.zone1_dht22_test.find(
        {"zone": zone, "area": area, "source": "pico_w", "ts": ts_query},
        {"_id": 0, "ts": 1, "temperature_c": 1, "humidity_rh": 1, "node_id": 1}
    ).sort("ts", 1))

    for d in docs:
        d["ts"] = d["ts"].isoformat()

    return jsonify(docs)

@app.route("/api/sensor/readings", methods=["GET"])
def get_sensor_readings():
    zone = request.args.get("zone", "zone1")
    area = request.args.get("area", "upper_plants")
    limit = request.args.get("limit", default=50, type=int)

    docs = list(
        db.zone1_dht22_test.find(
            {"zone": zone, "area": area, "source": "pico_w"}
        ).sort("ts", -1).limit(limit)
    )

    for d in docs:
        d["_id"] = str(d["_id"])
        d["ts"] = d["ts"].isoformat()

    return jsonify(docs)

if __name__ == "__main__":
    app.run(debug=True)