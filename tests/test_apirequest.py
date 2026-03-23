from datetime import datetime
from pathlib import Path
import importlib.util
import unittest
from unittest.mock import Mock, MagicMock, patch
import requests

# Resolve repo root and load backend module by file path.
ROOT = Path(__file__).resolve().parents[1]
APIREQUEST_PATH = ROOT / "backend" / "app" / "test" / "apirequest.py"

spec = importlib.util.spec_from_file_location("apirequest", APIREQUEST_PATH)
apirequest = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(apirequest)


class _FakeCollection:
    # Minimal Mongo-like stub to capture inserted documents.
    def __init__(self):
        self.inserted = []

    def insert_one(self, document):
        self.inserted.append(document)

    def create_index(self, field):
        self.indexed_field = field


class TestApiRequest(unittest.TestCase):
    def setUp(self):
        apirequest.collection = None

    def test_transform_data_maps_fields(self):
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
        self.assertEqual(record["area"], "upper_plants")
        self.assertEqual(record["source"], "openweather")
        self.assertEqual(record["sensor_type"], "weather")
        self.assertEqual(record["temp_c"], 21.3)
        self.assertEqual(record["humidity_pct"], 56)
        self.assertEqual(record["city"], "Akron")
        self.assertEqual(record["temp_min"], 20.1)
        self.assertEqual(record["temp_max"], 23.4)
        self.assertEqual(record["weather_desc"], "clear sky")
        self.assertIsInstance(record["ts"], datetime)

    def test_save_data_inserts_when_collection_exists(self):
        fake_collection = _FakeCollection()
        apirequest.collection = fake_collection

        payload = {"zone": "zone1", "temp_c": 22.0}
        apirequest.save_data(payload)

        self.assertEqual(len(fake_collection.inserted), 1)
        self.assertEqual(fake_collection.inserted[0], payload)

    def test_save_data_does_nothing_when_collection_is_none(self):
        apirequest.collection = None
        payload = {"zone": "zone1", "temp_c": 22.0}

        # Should not raise an error
        apirequest.save_data(payload)

        self.assertIsNone(apirequest.collection)

    @patch.object(apirequest.os, "getenv", return_value=None)
    def test_get_weather_returns_none_when_api_key_missing(self, mock_getenv):
        result = apirequest.get_weather()
        self.assertIsNone(result)

    @patch.object(apirequest.requests, "get")
    @patch.object(apirequest.os, "getenv", return_value="fake_api_key")
    def test_get_weather_returns_data_on_success(self, mock_getenv, mock_get):
        fake_response = Mock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.return_value = {
            "main": {
                "temp": 18.5,
                "humidity": 70,
                "temp_min": 17.0,
                "temp_max": 20.0,
            },
            "name": "Akron",
            "weather": [{"description": "cloudy"}],
        }
        mock_get.return_value = fake_response

        result = apirequest.get_weather()

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Akron")
        self.assertEqual(result["main"]["temp"], 18.5)
        mock_get.assert_called_once()

    @patch.object(apirequest.requests, "get", side_effect=requests.RequestException("API failed"))
    @patch.object(apirequest.os, "getenv", return_value="fake_api_key")
    def test_get_weather_returns_none_on_request_exception(self, mock_getenv, mock_get):
        result = apirequest.get_weather()
        self.assertIsNone(result)

    @patch.object(apirequest, "save_data")
    @patch.object(apirequest, "transform_data")
    @patch.object(apirequest, "get_weather")
    def test_collect_data_to_db_calls_transform_and_save(self, mock_get_weather, mock_transform, mock_save):
        fake_api_data = {
            "main": {"temp": 20, "humidity": 50, "temp_min": 19, "temp_max": 21},
            "name": "Akron",
            "weather": [{"description": "sunny"}],
        }
        fake_record = {"temp_c": 20}

        mock_get_weather.return_value = fake_api_data
        mock_transform.return_value = fake_record

        apirequest.collect_data_to_db()

        mock_get_weather.assert_called_once()
        mock_transform.assert_called_once_with(fake_api_data)
        mock_save.assert_called_once_with(fake_record)

    @patch.object(apirequest, "save_data")
    @patch.object(apirequest, "transform_data")
    @patch.object(apirequest, "get_weather", return_value=None)
    def test_collect_data_to_db_does_nothing_when_no_api_data(self, mock_get_weather, mock_transform, mock_save):
        apirequest.collect_data_to_db()

        mock_get_weather.assert_called_once()
        mock_transform.assert_not_called()
        mock_save.assert_not_called()

    @patch.object(apirequest.pymongo, "MongoClient")
    def test_init_db_collection_sets_collection_on_success(self, mock_client_class):
        fake_collection = _FakeCollection()

        fake_db = MagicMock()
        fake_db.__getitem__.return_value = fake_collection

        fake_client = MagicMock()
        fake_client.admin.command.return_value = {"ok": 1}
        fake_client.__getitem__.return_value = fake_db

        mock_client_class.return_value = fake_client

        apirequest.init_db_collection()

        self.assertEqual(apirequest.collection, fake_collection)
        self.assertEqual(fake_collection.indexed_field, "ts")

    @patch.object(apirequest.pymongo, "MongoClient", side_effect=Exception("DB failed"))
    def test_init_db_collection_sets_none_on_failure(self, mock_client_class):
        apirequest.init_db_collection()
        self.assertIsNone(apirequest.collection)


if __name__ == "__main__":
    unittest.main()