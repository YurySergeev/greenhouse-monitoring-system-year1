import random

class MockSensorNode:
    def __init__(self):
        #Construct baseline
        self.current_temp = 10.00
        self.current_humidity = 20.00

    def get_readings(self):
        
        # Simulate reading update
        self.current_temp += random(-1.5, 1.5)
        self.current_humidity += random(-1.5, 1.5)
        
        #
        #
        # DHT11 read goes here
        #
        #
        
        # Make sure humidity stays within physical 0-100% limits
        
        if(self.current_humidity < 0.00 or self.current_humidity > 100.00):
            self.current_humidity = 20.00
        
        

        return {
            
            "temperature_c": round(self.current_temp, 2),
            "humidity_rh": round(self.current_humidity, 2),
            "status": "ok_simulated"
            
        }