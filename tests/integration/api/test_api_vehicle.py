import pytest
from fuel_logger.models import Vehicle
from fuel_logger import db
import uuid


def test_vehicle_list(test_client, basic_auth_header):
    resp = test_client.get("/api/vehicles", headers=basic_auth_header)
    assert resp.status_code == 200
    assert len(resp.json) >= 1


def test_vehicle_get(test_client, basic_auth_header, test_vehicle_id, app_fixture):
    resp = test_client.get(
        f"/api/vehicles/{test_vehicle_id}", headers=basic_auth_header
    )
    assert resp.status_code == 200

    with app_fixture.app_context():
        test_vehicle = Vehicle.query.get(test_vehicle_id)

    assert test_vehicle.make == resp.json["make"]
    assert test_vehicle.model == resp.json["model"]
    assert test_vehicle.year == resp.json["year"]


def test_vehicle_create(test_client, basic_auth_header, app_fixture):
    # Define payload for new vehicle to be added
    random_model = f"TestModel-{uuid.uuid4()}"
    vehicle_payload = {
        "make": "TestMake",
        "model": random_model,
        "year": 1999,
    }

    # Ensure vehicle doesn't exist yet
    with app_fixture.app_context():
        assert (
            Vehicle.query.filter_by(
                make="TestMake",
                model=random_model,
                year=1999,
            ).count()
            == 0
        )

    # Make POST request to create new vehicle
    resp = test_client.post(
        "/api/vehicles", headers=basic_auth_header, json=vehicle_payload
    )

    # Assert new vehicle was created successfully and can be queried in database
    assert resp.status_code == 200
    assert resp.json.get("status") == "CREATED"
    with app_fixture.app_context():
        assert (
            Vehicle.query.filter_by(
                make="TestMake",
                model=random_model,
                year=1999,
            ).count()
            == 1
        )


def test_vehicle_create_empty(test_client, basic_auth_header, app_fixture):
    # Make POST request to create new vehicle
    resp = test_client.post("/api/vehicles", headers=basic_auth_header, json={})

    # Assert new vehicle was created successfully and can be queried in database
    assert resp.status_code == 400
    assert resp.json.get("error") == "Bad Request"
    assert "Missing data for required field" in resp.json.get("message")