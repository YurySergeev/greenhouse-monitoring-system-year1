from app.server import create_app, get_collection


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