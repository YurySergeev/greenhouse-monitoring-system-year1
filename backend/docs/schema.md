# Sensor Reading Schema

## Collection
weather_data

## Required Fields
- zone: greenhouse zone identifier
- area: specific section of the greenhouse
- source: origin of the data (e.g., openweather)
- sensor_type: type of data source
- temp_c: temperature in Celsius
- humidity_pct: humidity percentage
- ts: timestamp of reading (UTC)

## Optional Fields
- city: city name from API
- temp_min: minimum temperature
- temp_max: maximum temperature
- weather_desc: weather description

## Timestamp Format
- Stored in UTC
- Generated using:
  datetime.now(timezone.utc)

## Example Document
```json
{
  "zone": "zone1",
  "area": "upper_plants",
  "source": "openweather",
  "sensor_type": "weather",
  "temp_c": 0.47,
  "humidity_pct": 58,
  "city": "Akron",
  "temp_min": -0.48,
  "temp_max": 1.09,
  "weather_desc": "overcast clouds",
  "ts": "2026-03-18T23:41:24Z"
}

---

### ✅ Step 2: Run performance test
In terminal:

```bash
cd backend/app/test
python query_test.py