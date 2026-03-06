from datetime import datetime
import requests
import json
import pymongo
import schedule
import time


#fetch api from openweather API
def get_weather():

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat":41.0814,
        "lon":-81.5190,
        "appid":"9597cb5b6b7536f0f9d62e60a7978975",
         "units":"metric"

    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        print("weather:", data["weather"][0]["description"])
        print("Temperature:", data["main"]["temp"])
        print("temp_min:", data["main"]["temp_min"])
        print("temp_max:", data["main"]["temp_max"])
        print("Humidity:", data["main"]["humidity"])
        print("City",data["name"])
        print("Timestamp:", datetime.now())
        return data
    else:
        print("Error")
        return None


#dictionary that has attributes with data that will be saved into mongo
def transform_data(api_data):
    record = {
        "zone" : "zone1",
        "area" : "upper_plants",
        "source" : "openweather",
        "temp_c": api_data["main"]["temp"],
        "humidity_pct": api_data["main"]["humidity"],
        "city": api_data["name"],
        "temp_min": api_data["main"]["temp_min"],
        "temp_max": api_data["main"]["temp_max"],
        "weather_desc": api_data["weather"][0]["description"],
        "ts": datetime.now()
    }

    return record


#save data to mongo
def save_data(records):
    #connections
    MONGO_URI="mongodb+srv://rcoulson_db_user:7q6kDfRuldzW2COa@greenhouse-clouster.n6uuf84.mongodb.net/greenhouse_db?retryWrites=true&w=majority&appName=greenhouse-clouster"
    client = pymongo.MongoClient(MONGO_URI)
    db = client["greenhouse-clouster"]
    collection = db["weather_data"]
    collection.insert_one(records)
    print("data saved")

def collect_data_to_db():
    api_data = get_weather()
    final_data = transform_data(api_data)
    save_data(final_data)






# every 5 minutes, collect weather data,
# run through get_weather, transform_data, and save_data,
# then save to MongoDB forever until script is stopped
schedule.every(30).seconds.do(collect_data_to_db)

while True:
    schedule.run_pending()
    time.sleep(1)



'''
 to store data daily automatically 
 option 1 - leave the terminal running, dont close terminal 
 option 2 - deploy to cloud server,

 '''



