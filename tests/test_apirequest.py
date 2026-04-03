from datetime import datetime
from pathlib import Path
import importlib.util
import unittest

# Resolve repo root and load backend module by file path.
ROOT = Path(__file__).resolve().parents[1]
APIREQUEST_PATH = ROOT / "backend" / "app" / "test" / "apirequest.py"

spec = importlib.util.spec_from_file_location("apirequest", APIREQUEST_PATH)
apirequest = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(apirequest)


class _FakeCollection:
    
    def __init__(self):
        self.inserted = []

    def insert_one(self, document):
        self.inserted.append(document)


class TestApiRequest(unittest.TestCase):
    def test_transform_data_maps_fields(self):
        # Representative API payload shape from OpenWeather.
        api_data = {
            "main": {
                "temp": 21.3,
                "humidity": 56,
                "temp_min": 20.1,
                "temp_max": 23.4,
            },
            "name": "Akron",
            "weather": [{"description": "clear sky"}],
        }

        record = apirequest.transform_data(api_data)

        self.assertEqual(record["zone"], "zone1")
        self.assertEqual(record["source"], "openweather")
        self.assertEqual(record["temp_c"], 21.3)
        self.assertEqual(record["humidity_pct"], 56)
        self.assertEqual(record["city"], "Akron")
        self.assertEqual(record["weather_desc"], "clear sky")
        self.assertIsInstance(record["ts"], datetime)

    def test_save_data_inserts_when_collection_exists(self):
        # Inject fake collection so test does not depend on a real database.
        fake_collection = _FakeCollection()
        apirequest.collection = fake_collection

        payload = {"zone": "zone1", "temp_c": 22.0}
        apirequest.save_data(payload)

        self.assertEqual(len(fake_collection.inserted), 1)
        self.assertEqual(fake_collection.inserted[0], payload)


if __name__ == "__main__":
    unittest.main()
