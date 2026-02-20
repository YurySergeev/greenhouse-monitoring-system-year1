from flask import Flask, request, jsonify

app = Flask(__name__)

# This route listens for POST requests at the /data endpoint
@app.route('/data', methods=['POST'])
def receive_data():
    # Parse the incoming JSON from the Pico W
    incoming_json = request.get_json()
    
    # Print it to the computer's terminal so you can see it working
    print(f"Data received from greenhouse: {incoming_json}")
    
    # Send a success message back to the Pico
    return jsonify({"status": "success", "message": "Data logged safely"}), 200

if __name__ == '__main__':
    # host='0.0.0.0' is CRITICAL. It allows devices on your local Wi-Fi 
    # to access this server, not just your local machine.
    app.run(host='0.0.0.0', port=5000)
    while True:
        receive_data()
    
