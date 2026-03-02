from app.services.openweather_service import fetch_and_store

def run_openweather_job():
    print("[JOB] OpenWeather job running...")
    fetch_and_store(zone="zone1", area="upper_plants", source="openweather")
    print("[JOB] OpenWeather job finished ")