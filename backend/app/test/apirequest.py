import requests

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


        print("Temperature:", data["main"]["temp"])
        print("Humidity:", data["main"]["humidity"])
    else:
        print("Error")

    print(response.status_code)
    print(response.json())

