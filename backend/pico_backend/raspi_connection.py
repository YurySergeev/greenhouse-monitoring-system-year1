import network
import time
import dht
import machine
import urequests # requests library

# --- Requirements ---
# Pico w and Server must be on the same Network
# Server_URL = server IPv4 address --- find via ipconfig(windows)

# --- Configuration ---
SSID = "MyNet"
PASSWORD = "123456789"


# ipconfig in cmd to find your ip
SERVER_URL = "http://10.123.164.137:5000/data" 

# Initialize the DHT11 sensor
#-------Temporary sensor comment out
#sensor = dht.DHT11(machine.Pin(15))
led = machine.Pin("LED", machine.Pin.OUT)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to WiFi...")
    
    while not wlan.isconnected():
        led.toggle()
        time.sleep(0.5)
        
    led.on()
    print(f"Connected! Pico IP: {wlan.ifconfig()[0]}")




def send_telemetry(temp, humidity):
    try:
        # Trigger the sensor to take a reading
        #sensor.measure()
        temp_c = temp
        humidity = humidity
        
        # Package the data into a JSON dictionary
        payload = {
            "node_id": "pico_prototype_1",
            "temperature_c": temp_c,
            "humidity_rh": humidity
        }
        
        print(f"Sending to server: {payload}")
        
        # Send the HTTP POST request
        response = urequests.post(SERVER_URL, json=payload)
        print(f"Server replied with status: {response.status_code}")
        
        # CRITICAL: Always close the response to free up Pico memory
        response.close() 
        
    except OSError as e:
        print("Failed to read sensor. Check wiring!")
    except Exception as e:
        print(f"Network error: {e}")

# --- Main Execution Loop ---
connect_wifi()

while True:
    send_telemetry()
    time.sleep(10) # Send data every 10 seconds for testing
