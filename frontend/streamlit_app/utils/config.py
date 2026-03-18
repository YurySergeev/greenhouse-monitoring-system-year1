#THIS FILE CONTAIN KEYS
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_KEY   = (os.getenv("OPENWEATHER_API_KEY") or "").strip()
MONGO_URI = (os.getenv("MONGO_URI") or "").strip()
DB_NAME   = (os.getenv("DB_NAME") or "").strip()

CITY = "Akron,US"