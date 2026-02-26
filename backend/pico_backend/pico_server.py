from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Mock URL for testing purposes (replace with Casini's API URL when ready)
MOCK_CASINI_URL = "http://localhost:5001/mock-casini-endpoint"  # Mock URL for testing

@app.route('/data', methods=['POST'])
def receive_data():
    """
    Receives data from Raspberry Pi, adds a timestamp, and forwards it to a mock Casini endpoint.
    """
    incoming_json = request.get_json()

    if not incoming_json:
        return jsonify({"status": "error", "message": "No data received"}), 400

    # Print received data for debugging
    print(f"Data received: {incoming_json}")

    # Add timestamp to the incoming data
    incoming_json["timestamp"] = datetime.utcnow().isoformat()

    # Mock forward data to Casini (or replace this with actual Casini endpoint)
    try:
        # Send the data to a mock endpoint (you will replace this URL with Casini when it's available)
        response = requests.post(MOCK_CASINI_URL, json=incoming_json)
        print(f"Data forwarded to mock Casini: {response.status_code}")
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Data forwarded successfully to mock Casini"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to forward data to mock Casini"}), 500
    except requests.exceptions.RequestException as e:
        print(f"Error forwarding data: {e}")
        return jsonify({"status": "error", "message": "Failed to connect to mock Casini"}), 500

if __name__ == '__main__':
    # Ensure the server is accessible from devices on the local network
    app.run(host='0.0.0.0', port=5000)
    print("Server started on http://0.0.0.0:5000 ...")