import pytest
from app.server import create_app, get_collection
from unittest.mock import MagicMock, patch


# -----------------------------
# BASIC ROUTE TESTS
# -----------------------------

def test_api_test_route():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/test")

    assert response.status_code == 200
    assert b"FLASK TEST OK" in response.data


def test_post_sensor_data():
    app = create_app()
    client = app.test_client()

    response = client.post("/api/sensor-data", json={
        "temp_c": 25,
        "humidity_pct": 60
    })

    assert response.status_code == 201


def test_db_connection():
    collection = get_collection()
    assert collection is not None


# -----------------------------
# VALIDATION TESTS
# -----------------------------

def test_post_sensor_data_missing_fields():
    app = create_app()
    client = app.test_client()

    response = client.post("/api/sensor-data", json={
        "temp_c": 25
        # missing humidity_pct
    })

    assert response.status_code == 400


def test_post_sensor_data_invalid_json():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/sensor-data",
        data="not-json",
        content_type="application/json"
    )

    assert response.status_code == 400


# -----------------------------
# GET ROUTE TESTS
# -----------------------------

def test_get_sensor_data():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/sensor-data")

    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_sensor_data_invalid_id():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/sensor-data/invalid-id")

    assert response.status_code == 400


def test_get_sensor_data_not_found():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/sensor-data/66f000000000000000000000")

    assert response.status_code == 404


# -----------------------------
# MOCKED DATABASE TESTS
# -----------------------------

def test_post_sensor_data_db_insert_mocked():
    app = create_app()
    client = app.test_client()

    with patch("app.server.get_collection") as mock_get_collection:
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        response = client.post("/api/sensor-data", json={
            "temp_c": 22,
            "humidity_pct": 55
        })

        assert response.status_code == 201
        mock_collection.insert_one.assert_called_once()


def test_db_connection_failure():
    with patch("pymongo.MongoClient") as mock_client:
        mock_client.side_effect = Exception("DB down")

        collection = get_collection()
        assert collection is None
