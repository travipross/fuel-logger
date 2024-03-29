import uuid

import pytest

from fuel_logger import db
from fuel_logger.models import Vehicle


@pytest.fixture
def vehicle_id_to_delete(app_fixture):
    # Create vehicle object
    with app_fixture.app_context():
        random_model = f"TestModel-{uuid.uuid4()}"
        vehicle = Vehicle(
            make="TestMake",
            model=random_model,
            year=2000,
        )
        db.session.add(vehicle)
        db.session.commit()
        yield vehicle.id

    # delete at teardown if object still exists
    with app_fixture.app_context():
        if db.session.get(Vehicle, vehicle.id) is not None:
            db.session.delete(vehicle)
            db.session.commit()


def test_vehicle_list(test_client, basic_auth_header):
    # Confirm that a non-empty list of vehicles is returned by the API
    resp = test_client.get("/api/vehicles", headers=basic_auth_header)
    assert resp.status_code == 200
    assert len(resp.json) >= 1


def test_vehicle_get(test_client, basic_auth_header, test_vehicle_id, app_fixture):
    # request specific vehicle by id
    resp = test_client.get(
        f"/api/vehicles/{test_vehicle_id}", headers=basic_auth_header
    )
    assert resp.status_code == 200

    # Confirm vehicle details returned by the api match what is expected
    with app_fixture.app_context():
        test_vehicle = db.session.get(Vehicle, test_vehicle_id)

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
            db.session.scalar(
                db.select(db.func.count(Vehicle.id)).filter_by(
                    make="TestMake",
                    model=random_model,
                    year=1999,
                )
            )
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


def test_vehicle_create_empty(test_client, basic_auth_header):
    # Make POST request to create new vehicle
    resp = test_client.post("/api/vehicles", headers=basic_auth_header, json={})

    # Assert new vehicle was created successfully and can be queried in database
    assert resp.status_code == 400
    assert resp.json.get("error") == "Bad Request"
    assert "Missing data for required field" in resp.json.get("message")


def test_vehicle_delete(
    test_client, basic_auth_header, app_fixture, vehicle_id_to_delete
):
    # Ensure vehicle exists
    with app_fixture.app_context():
        assert db.session.get(Vehicle, vehicle_id_to_delete) is not None

    # Make HTTP DELETE request
    resp = test_client.delete(
        f"/api/vehicles/{vehicle_id_to_delete}", headers=basic_auth_header
    )

    # Assert API responded correctly
    assert resp.status_code == 200
    assert resp.json.get("status") == "DELETED"

    # Confirm vehicle no longer exists in database
    with app_fixture.app_context():
        assert db.session.get(Vehicle, vehicle_id_to_delete) is None


def test_vehicle_get_favourite(
    test_client, basic_auth_header, app_fixture, test_vehicle_id
):
    # Ensure vehicle exists
    with app_fixture.app_context():
        assert db.session.get(Vehicle, test_vehicle_id) is not None

    # Make HTTP GET request
    resp = test_client.get(f"/api/fav_vehicle", headers=basic_auth_header)

    # Assert API responded correctly
    assert resp.status_code == 200
    assert resp.json.get("id") == test_vehicle_id


@pytest.fixture
def unset_favourite_vehicle(test_vehicle_id, app_fixture):
    with app_fixture.app_context():
        v = db.session.get(Vehicle, test_vehicle_id)
        v.is_favourite = False
        db.session.commit()
        yield

    with app_fixture.app_context():
        v = db.session.get(Vehicle, test_vehicle_id)
        v.is_favourite = True
        db.session.commit()


@pytest.mark.usefixtures("unset_favourite_vehicle")
def test_vehicle_get_favourite_none_found(
    test_client, basic_auth_header, app_fixture, test_vehicle_id
):
    # Ensure vehicles exist or not
    with app_fixture.app_context():
        assert db.session.get(Vehicle, test_vehicle_id) is not None

    # Make HTTP GET request
    resp = test_client.get(f"/api/fav_vehicle", headers=basic_auth_header)

    # Assert API responded correctly
    assert resp.status_code == 404
    assert resp.json.get("message") == "Vehicle not found."


def test_vehicle_set_favourite(
    test_client, basic_auth_header, app_fixture, test_vehicle_id, test_vehicle_id_alt
):
    # Ensure vehicle exists
    with app_fixture.app_context():
        vehicle = db.session.get(Vehicle, test_vehicle_id)
        vehicle_alt = db.session.get(Vehicle, test_vehicle_id_alt)

        assert vehicle is not None
        assert vehicle.is_favourite == True

        assert vehicle_alt is not None
        assert vehicle_alt.is_favourite == False

    # Make HTTP POST request
    resp = test_client.post(
        f"/api/fav_vehicle", headers=basic_auth_header, json={"id": test_vehicle_id_alt}
    )

    # Assert API responded correctly
    assert resp.status_code == 200
    assert resp.json.get("status") == "UPDATED"

    # Asset db record is updated
    with app_fixture.app_context():
        vehicle = db.session.get(Vehicle, test_vehicle_id)
        vehicle_alt = db.session.get(Vehicle, test_vehicle_id_alt)

        assert vehicle is not None
        assert vehicle.is_favourite == False

        assert vehicle_alt is not None
        assert vehicle_alt.is_favourite == True


def test_vehicle_set_favourite_invalid(
    test_user_id, secondary_vehicle_id_1, test_client, basic_auth_header, app_fixture
):
    # Ensure vehicle exists and is owned by someone else
    with app_fixture.app_context():
        vehicle = db.session.get(Vehicle, secondary_vehicle_id_1)
        assert vehicle is not None
        assert vehicle.owner_id != test_user_id

    # Make HTTP POST request
    resp = test_client.post(
        f"/api/fav_vehicle",
        headers=basic_auth_header,
        json={"id": secondary_vehicle_id_1},
    )

    # Assert API responded correctly
    assert resp.status_code == 200
    assert resp.json.get("status") == "error"
