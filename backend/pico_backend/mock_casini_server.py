# mock_casini_server.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    """
    Mock endpoint to receive data from the MacBook collection point.
    This would forward the data to the MongoDB database.
    """
    incoming_data = request.get_json()

    if not incoming_data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    # Print the received data to simulate logging the data to a database
    print(f"Received data: {incoming_data}")

    # Simulate the success of storing data in a database
    return jsonify({"status": "success", "message": "Data received and stored successfully"}), 200

if __name__ == '__main__':
    # Run the mock server on a different port (e.g., 5001) for testing
    app.run(host='0.0.0.0', port=5001)