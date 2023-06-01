from fuel_logger import db
from fuel_logger.models import User, Vehicle


def test_garage__default(app_fixture, test_user_id, test_username):
    # Logged in user accessing own garage
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(f"/garage", follow_redirects=True)

        assert resp.status_code == 200
        assert f"{test_username}'s Garage" in resp.text


def test_garage__unauthenticated(test_client):
    # Prompt for sign-in when unauthenticated
    resp = test_client.get(f"/garage", follow_redirects=True)
    assert resp.status_code == 200
    assert 302 in [r.status_code for r in resp.history]
    assert f"Sign In" in resp.text


def test_set_fav_vehicle__exists(
    app_fixture, test_user_id, test_vehicle_id, secondary_vehicle_id
):

    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        test_vehicle = db.session.get(Vehicle, test_vehicle_id)
        secondary_vehicle = db.session.get(Vehicle, secondary_vehicle_id)

        # set initial favourite vehicle
        test_user.set_favourite_vehicle(test_vehicle)

        # Confirm initial favourite vehicle
        assert test_vehicle.is_favourite == True
        assert secondary_vehicle.is_favourite == False

        # test endpoint
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/set_fav_vehicle/{secondary_vehicle_id}",
                follow_redirects=True,
            )

        assert resp.status_code == 200

        # Confirm new favourite vehicle
        assert test_vehicle.is_favourite == False
        assert secondary_vehicle.is_favourite == True


def test_set_fav_vehicle__nonexistent(
    app_fixture, test_user_id, test_vehicle_id, test_username
):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)

        # confirm bad vehicle doesn't exist
        bad_vehicle_id = test_vehicle_id + 69
        assert db.session.get(Vehicle, bad_vehicle_id) is None

        # Attempt to set favourite with nonexistent vehicle id
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/set_fav_vehicle/{bad_vehicle_id}",
                follow_redirects=True,
            )

        # Redirect to garage page and flash message
        assert resp.status_code == 200
        assert "invalid vehicle" in resp.text
        assert f"{test_username}'s Garage" in resp.text


def test_add_vehicle__unauthenticated(test_client):
    # redirect to sign-in page if not logged in
    resp = test_client.get(f"/add_vehicle", follow_redirects=True)
    assert resp.status_code == 200
    assert 302 in [r.status_code for r in resp.history]
    assert f"Sign In" in resp.text


def test_add_vehicle__get(app_fixture, test_user_id):
    # Confirm correct page is returned when logged in
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/add_vehicle",
                follow_redirects=True,
            )

        assert resp.status_code == 200
        assert "Add Vehicle" in resp.text


def test_add_vehicle__post_complete(app_fixture, test_user_id):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)

        # Confirm the new vehicle doesn't exist yet
        assert test_user.vehicles.filter(Vehicle.make == "FormTestMake").count() == 0

        # Add new vehicle
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

        # Confirm request was successful
        assert resp.status_code == 200
        assert f"Your vehicle has been added" in resp.text

        # Confirm new vehicle exists with correct data
        assert test_user.vehicles.filter(Vehicle.make == "FormTestMake").count() == 1
        new_vehicle = test_user.vehicles.filter(Vehicle.make == "FormTestMake").one()
        assert new_vehicle.make == "FormTestMake"
        assert new_vehicle.model == "FormTestModel"
        assert new_vehicle.year == 2345
        assert new_vehicle.odo_unit == "km"
