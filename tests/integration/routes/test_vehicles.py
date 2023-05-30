from fuel_logger.models import User, Vehicle
from fuel_logger import db
import pytest


def test_garage__default(app_fixture, test_user_id, test_username):
    with app_fixture.app_context():
        test_user = User.query.get(test_user_id)

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/garage/{test_user_id}", follow_redirects=True
            )

        assert resp.status_code == 200
        assert f"{test_username}'s Garage" in resp.text


def test_garage__random_user_garage(app_fixture, test_user_id):
    with app_fixture.app_context():
        test_user = User.query.get(test_user_id)

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/garage/{test_user_id}abcdefg", follow_redirects=True
            )

        assert resp.status_code == 403
        assert f"Unauthorized" in resp.text


def test_garage__unauthenticated(test_client, test_user_id):
    resp = test_client.get(f"/garage/{test_user_id}", follow_redirects=True)
    assert resp.status_code == 200
    assert 302 in [r.status_code for r in resp.history]
    assert f"Sign In" in resp.text


@pytest.fixture
def secondary_vehicle_id(app_fixture, test_user_id):
    v = Vehicle(
        make="MadeUpMake",
        model="MadeUpModel",
        year="1234",
    )
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        user.vehicles.append(v)
        db.session.flush()
        assert v.is_favourite == False
        db.session.commit()
        yield v.id

    with app_fixture.app_context():
        db.session.delete(v)
        db.session.commit()


def test_set_fav_vehicle__exists(
    app_fixture, test_user_id, test_vehicle_id, secondary_vehicle_id
):
    with app_fixture.app_context():
        test_user = User.query.get(test_user_id)
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/set_fav_vehicle/{test_user_id}/{test_vehicle_id}",
                follow_redirects=True,
            )

        assert resp.status_code == 200

        with app_fixture.app_context():
            user = User.query.get(test_user_id)
            assert user.get_favourite_vehicle().id == test_vehicle_id

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/set_fav_vehicle/{test_user_id}/{secondary_vehicle_id}",
                follow_redirects=True,
            )

        assert resp.status_code == 200

        with app_fixture.app_context():
            user = User.query.get(test_user_id)
            assert user.get_favourite_vehicle().id == secondary_vehicle_id


def test_add_vehicle__unauthenticated(test_client):
    resp = test_client.get(f"/add_vehicle", follow_redirects=True)
    assert resp.status_code == 200
    assert 302 in [r.status_code for r in resp.history]
    assert f"Sign In" in resp.text


def test_add_vehicle__get(app_fixture, test_user_id):
    with app_fixture.app_context():
        test_user = User.query.get(test_user_id)
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/add_vehicle",
                follow_redirects=True,
            )

        assert resp.status_code == 200
        assert "Add Vehicle" in resp.text


def test_add_vehicle__post_complete(app_fixture, test_user_id, test_vehicle_id):
    with app_fixture.app_context():
        test_user = User.query.get(test_user_id)

        assert test_user.vehicles.filter(Vehicle.id != test_vehicle_id).count() == 0

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.post(
                "/add_vehicle",
                follow_redirects=True,
                data={
                    "make": "FormTestMake",
                    "model": "FormTestModel",
                    "year": 2345,
                    "odo_unit": "km",
                },
            )

        assert resp.status_code == 200
        assert f"Your vehicle has been added" in resp.text

        assert test_user.vehicles.filter(Vehicle.id != test_vehicle_id).count() == 1
        new_vehicle = test_user.vehicles.filter(Vehicle.id != test_vehicle_id).one()

        assert new_vehicle.make == "FormTestMake"
        assert new_vehicle.model == "FormTestModel"
        assert new_vehicle.year == 2345
        assert new_vehicle.odo_unit == "km"
