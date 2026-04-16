from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "greenhouse_db")

#get collection to db
def get_collection():
    if not MONGO_URI:
        print("ERROR: MONGO_URI is missing")   # changed
        return None                            # changed
        #raise ValueError("MONGO_URI is missing") #if db address missing throw error


    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) #connect to mongo
    client.admin.command("ping") #ping it = makes sure answer
    db = client[DB_NAME] #get into the db
    return db["sensor_data"] #return the sensor_Data collection


def create_app():
    app = Flask(__name__) #build server

    @app.route("/api/test", methods=["GET"]) #visit the server
    def test():
        return jsonify({"message": "FLASK TEST OK"}), 200 #checks

    @app.route("/api/sensor-data", methods=["POST"]) #receive sensor data,
    def receive_sensor_data():
        try:
            data = request.get_json(silent=True) #reads JSON that is sent

            #if not data:
            if data is None:
                return jsonify({"error": "No JSON received"}), 400 #if nothing is sent
            # if temp_c or humidity_pct not found 
            if "temp_c" not in data or "humidity_pct" not in data:
                return jsonify({"error": "Missing required fields"}), 400
            # add extra fields into db before saving where is the sensor
            data["zone"] = "zone1"
            data["area"] = "upper_plants"
            data["sensor_id"] = "test_sensor_01"
            data["ts"] = datetime.now(timezone.utc)

            collection = get_collection() #gets to mongo collectio
            result = collection.insert_one(data) #saves data

            print("Saved data:", data)

            #sends back a 201
            return jsonify({
                "message": "Data saved",
                "inserted_id": str(result.inserted_id)
            }), 201

        #something is wrong
        except Exception as e:
            print("ERROR:", e)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/readings/latest", methods=["GET"])
    def get_latest_reading():
        try:
            collection = get_collection()
            latest = collection.find_one(sort=[("ts", -1)])

            if not latest:
                return jsonify({"error": "No data found"}), 404

            latest["_id"] = str(latest["_id"])

            return jsonify(latest), 200

        except Exception as e:
            print("ERROR:", e)
            return jsonify({"error": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5050, debug=True)