# backend/app/auto_ingest/pull_openweather.py

import time
from app.ingest_openweather_live import fetch_and_store

INTERVAL = 15 * 60  # 15 minutes

def main():
    while True:
        fetch_and_store()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()