import pytest
from fuel_logger import db
from fuel_logger.models import Vehicle, Fillup


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
