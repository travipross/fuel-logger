import pytest

from fuel_logger import db
from fuel_logger.models import Fillup, Vehicle


@pytest.fixture
def sample_fillup_ids(app_fixture, test_vehicle_id):
    with app_fixture.app_context():
        vehicle = db.session.get(Vehicle, test_vehicle_id)
        # confirm initially empty
        assert vehicle.fillups.count() == 0

        # Add some sample fillups
        vehicle.fillups.extend(
            [
                Fillup(
                    odometer_km=100,
                    fuel_amt_l=6,
                ),
                Fillup(
                    odometer_km=200,
                    fuel_amt_l=7,
                ),
                Fillup(
                    odometer_km=300,
                    fuel_amt_l=8,
                ),
            ]
        )
        db.session.commit()
        fillup_ids = [f.id for f in vehicle.fillups]
        yield fillup_ids

    # Delete fillups
    with app_fixture.app_context():
        db.session.execute(db.delete(Fillup).where(Fillup.id.in_(fillup_ids)))
        db.session.commit()
        # Confirm deletion was successful
        assert (
            db.session.scalar(
                db.select(db.func.count(Fillup.id)).where(Fillup.id.in_(fillup_ids))
            )
            == 0
        )


def test_get_logs__no_vehicle_id(test_client, basic_auth_header):
    # Empty response returned when no logs exist
    resp = test_client.get("/api/logs", headers=basic_auth_header)
    assert resp.status_code == 200
    assert resp.json == []


def test_get_logs(test_client, basic_auth_header, test_vehicle_id, sample_fillup_ids):
    # Check that the correct logs are returned for the given vehicle
    resp = test_client.get(
        f"/api/logs?vehicle_id={test_vehicle_id}", headers=basic_auth_header
    )
    assert resp.status_code == 200
    assert len(resp.json) == 3
    assert set(sample_fillup_ids) == {f.get("id") for f in resp.json}


def test_get_log_by_id(test_client, basic_auth_header, sample_fillup_ids):
    resp = test_client.get(
        f"/api/logs/{sample_fillup_ids[0]}",
        headers=basic_auth_header,
    )

    assert resp.status_code == 200
    assert resp.json.get("id") == sample_fillup_ids[0]
    assert resp.json.get("fuel_amt_l") == 6
    assert resp.json.get("odometer_km") == 100


def test_get_log_by_id__non_existent(test_client, basic_auth_header):
    resp = test_client.get(
        f"/api/logs/1234",
        headers=basic_auth_header,
    )

    assert resp.status_code == 404
    assert resp.json.get("message") == "No log by that ID found."


def test_pose_log__valid(app_fixture, test_client, basic_auth_header, test_vehicle_id):
    resp = test_client.post(
        f"/api/logs?vehicle_id={test_vehicle_id}",
        headers=basic_auth_header,
        json={
            "odometer_km": 1234,
            "fuel_amt_l": 69,
        },
    )

    assert resp.status_code == 200
    assert resp.json.get("odometer_km") == 1234
    id = resp.json.get("id")
    assert id is not None

    # clean up
    with app_fixture.app_context():
        fillup = db.session.get(Fillup, id)
        db.session.delete(fillup)
        db.session.commit()


def test_pose_log__bad_payload(test_client, basic_auth_header, test_vehicle_id):
    resp = test_client.post(
        f"/api/logs?vehicle_id={test_vehicle_id}",
        headers=basic_auth_header,
        json={
            "odometer_km": 1234,
            "fuel_amt_l": 69,
            "banana": 1234,
        },
    )

    assert resp.status_code == 500
    assert resp.json.get("error") == "Internal Server Error"
    assert "banana" in resp.json.get("message")


def test_pose_log__no_vehicle(test_client, basic_auth_header):
    resp = test_client.post(
        f"/api/logs",
        headers=basic_auth_header,
        json={
            "odometer_km": 1234,
            "fuel_amt_l": 69,
        },
    )

    assert resp.status_code == 400
    assert resp.json.get("message") == "missing vehicle_id query parameter"
