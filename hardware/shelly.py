from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["shelly_data"]
collection = db["ht_readings"]


@app.route("/")
def home():
    return jsonify({"message": "Server is running. Use /api/shelly"}), 200


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/shelly", methods=["GET", "POST"])
def receive_shelly():
    try:
        # Fetch data from the request (either GET or POST)
        data = request.args.to_dict()

        if not data and request.is_json:
            data = request.get_json()

        # Handle the case where no data is received
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # Print incoming data for debugging
        print("Incoming Shelly data:", data)

        # Extract data (temperature, humidity, battery)
        temp = data.get("temp") or data.get("temperature")
        hum = data.get("hum") or data.get("humidity")
        battery = data.get("bat") or data.get("battery")

        # Create the record to store in MongoDB
        record = {
            "sensor_id": "shelly_ht",
            "timestamp": datetime.now(timezone.utc),
            "raw": data
        }

        # Only insert non-null values
        if temp is not None:
            record["temperature"] = float(temp)
        if hum is not None:
            record["humidity"] = float(hum)
        if battery is not None:
            record["battery"] = int(battery)

        # Insert the record into MongoDB
        result = collection.insert_one(record)

        # Return the stored data with the new document ID
        return jsonify({
            "status": "success",
            "data": {
                "id": str(result.inserted_id),
                "sensor_id": record["sensor_id"],
                "temperature": record.get("temperature"),
                "humidity": record.get("humidity"),
                "battery": record.get("battery"),
                "timestamp": record["timestamp"].isoformat()
            }
        }), 200

    except Exception as e:
        # Handle errors by returning the exception message
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/latest", methods=["GET"])
def get_latest():
    try:
        # Find the latest document with temperature, humidity, and battery
        latest_temp = collection.find_one(
            {"sensor_id": "shelly_ht", "temperature": {"$ne": None}},
            sort=[("timestamp", -1)]
        )

        latest_hum = collection.find_one(
            {"sensor_id": "shelly_ht", "humidity": {"$ne": None}},
            sort=[("timestamp", -1)]
        )

        latest_battery = collection.find_one(
            {"sensor_id": "shelly_ht", "battery": {"$ne": None}},
            sort=[("timestamp", -1)]
        )

        # If no data exists, return an error message
        if not latest_temp and not latest_hum and not latest_battery:
            return jsonify({"status": "error", "message": "No data"}), 404

        # Calculate the most recent timestamp
        latest_timestamp = None
        timestamps = [
            doc["timestamp"]
            for doc in [latest_temp, latest_hum, latest_battery]
            if doc and "timestamp" in doc
        ]
        if timestamps:
            latest_timestamp = max(timestamps).isoformat()

        # Return the most recent data
        return jsonify({
            "sensor_id": "shelly_ht",
            "temperature": latest_temp["temperature"] if latest_temp else None,
            "humidity": latest_hum["humidity"] if latest_hum else None,
            "battery": latest_battery["battery"] if latest_battery else None,
            "timestamp": latest_timestamp
        }), 200

    except Exception as e:
        # Handle errors and return an error message
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/all", methods=["GET"])
def get_all():
    try:
        # Get the latest 50 records with sensor_id = shelly_ht
        docs = list(
            collection.find({"sensor_id": "shelly_ht"}).sort("timestamp", -1).limit(50)
        )

        # Format the documents for JSON response
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            doc["timestamp"] = doc["timestamp"].isoformat()

        # Return all records
        return jsonify(docs), 200

    except Exception as e:
        # Handle errors and return an error message
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    # Run the Flask app on all network interfaces
    app.run(host="0.0.0.0", port=5000)