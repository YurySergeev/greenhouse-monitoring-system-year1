# Greenhouse Monitoring System – Backend

###  Stack
- Python
- MongoDB Atlas
- OpenWeather API
- pymongo
- dotenv

-This backend service is responsible for:
-   Fetching live weather data from OpenWeather API
  -   Storing weather readings in MongoDB
- Updating today's document (no duplicates per day)

## Requirements

- Python 3.10+
- pip
- MongoDB Atlas account (or local MongoDB)

# Setup Instructions

### 1 - Clone the repository
 git clone <your-repo-url>
 cd greenhouse-monitoring-system/backend

### 2 - Create virtual environment
 python -m venv .venv
 
### 3 - activate 
source .venv/bin/activate

### 4- install dependenncies 
pip install -r requirements.txt


###  5-Create .env file
MONGO_URI=your_mongodb_connection_string
DB_NAME=greenhouse_db

OPENWEATHER_API_KEY=your_openweather_api_key
OPENWEATHER_CITY=Akron
OPENWEATHER_COUNTRY=US
OPENWEATHER_UNITS=metric

ZONE=zone1


### 6-run back end 
python -m app.ingest_openweather_live