from fuel_logger.models import User, Vehicle, Fillup
from fuel_logger import db
import pytest
from datetime import datetime
import pandas as pd
import io


def test_logs__get(
    app_fixture, test_user_id, test_username, test_vehicle_id, sample_fillup_ids
):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        test_vehicle = db.session.get(Vehicle, test_vehicle_id)

        assert test_vehicle.fillups.count() == 2
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/logs/{test_vehicle_id}", follow_redirects=True
            )

        assert resp.status_code == 200
        assert f"{test_username}'s 2017 Honda (Test) Civic (Test)" in resp.text
        assert "Fuel Stats" in resp.text


@pytest.fixture
def temp_person_id(app_fixture):
    with app_fixture.app_context():
        user = User(username="tempperson", email="temp-person@person.com")
        db.session.add(user)
        db.session.commit()
        yield user.id
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def temp_vehicle_id(app_fixture, temp_person_id):
    with app_fixture.app_context():
        vehicle = Vehicle(
            make="tempmake", model="tempmodel", year="2018", owner_id=temp_person_id
        )
        db.session.add(vehicle)
        db.session.commit()
        yield vehicle.id
        db.session.delete(vehicle)
        db.session.commit()


@pytest.fixture
def temp_fillup_id(app_fixture, temp_vehicle_id):
    with app_fixture.app_context():
        fillup = Fillup(
            timestamp=datetime.now(),
            odometer_km=234,
            fuel_amt_l=123,
            vehicle_id=temp_vehicle_id,
        )
        db.session.add(fillup)
        db.session.commit()
        yield fillup.id
        db.session.delete(fillup)
        db.session.commit()


def test_logs__other_user_error(app_fixture, test_user_id, temp_vehicle_id):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/logs/{temp_vehicle_id}",
                follow_redirects=True,
                headers={"Accept": "text/html"},
            )

        assert resp.status_code == 403
        assert "You have no access to these logs" in resp.text


def test_logs__other_user_error__json(app_fixture, test_user_id, temp_vehicle_id):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/logs/{temp_vehicle_id}", follow_redirects=True
            )

        assert resp.status_code == 403
        assert resp.json == {
            "error": "Forbidden",
            "message": "403 Forbidden: You have no access to these logs",
        }


def test_logs__post(app_fixture, test_user_id, test_vehicle_id):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        test_vehicle = db.session.get(Vehicle, test_vehicle_id)

        assert test_vehicle.fillups.count() == 0
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.post(
                f"/logs/{test_vehicle_id}",
                follow_redirects=True,
                data={
                    "odometer": 500,
                    "fuel": 20,
                    "date": "2020-04-20",
                    "time": "4:20",
                },
            )

        assert resp.status_code == 200
        assert "Your fuel log has been updated" in resp.text

        assert test_vehicle.fillups.count() == 1

        # cleanup
        test_vehicle.fillups.delete()
        db.session.commit()


def test_logs__post_invalid(
    app_fixture, test_user_id, test_vehicle_id, sample_fillup_id_1
):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        test_vehicle = db.session.get(Vehicle, test_vehicle_id)

        assert test_vehicle.fillups.count() == 1
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.post(
                f"/logs/{test_vehicle_id}",
                follow_redirects=True,
                data={
                    "odometer": 1,
                    "fuel": 20,
                    "date": "2020-04-20",
                    "time": "asdgasdfasdf",
                },
            )

        assert resp.status_code == 200
        assert "Your fuel log has been updated" not in resp.text

        assert test_vehicle.fillups.count() == 1


def test_logs__delete(
    app_fixture, test_vehicle_id, test_user_id, sample_fillup_id_1, sample_fillup_ids
):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        sample_vehicle = db.session.get(Vehicle, test_vehicle_id)

        assert sample_vehicle.fillups.count() == 2
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.delete(
                f"/logs/delete/{sample_fillup_id_1}"
            )

        assert resp.status_code == 200
        assert sample_vehicle.fillups.count() == 1


def test_logs__delete_error(
    app_fixture,
    test_vehicle_id,
    test_user_id,
    sample_fillup_id_1,
    sample_fillup_ids,
    temp_fillup_id,
    mocker,
):
    mocked_fn = mocker.MagicMock(
        "fuel_logger.fuel_logs.routes.db.session.commit", side_effect=Exception
    )
    mocker.patch("fuel_logger.fuel_logs.routes.db.session.commit", mocked_fn)
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        sample_vehicle = db.session.get(Vehicle, test_vehicle_id)

        assert sample_vehicle.fillups.count() == 2
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.delete(
                f"/logs/delete/{sample_fillup_id_1}"
            )

        assert resp.status_code == 500
        assert sample_vehicle.fillups.count() == 2

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.delete(
                f"/logs/delete/{sample_fillup_id_1+69420}"
            )

        assert resp.status_code == 404
        assert sample_vehicle.fillups.count() == 2

        # Try with someone else's vehicle
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.delete(f"/logs/delete/{temp_fillup_id}")
        assert resp.status_code == 403
        assert "You have no access to these logs" in resp.text


def test_logs__bulk_delete(
    app_fixture, test_vehicle_id, test_user_id, sample_fillup_id_1, sample_fillup_ids
):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        sample_vehicle = db.session.get(Vehicle, test_vehicle_id)

        assert sample_vehicle.fillups.count() == 2
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.delete(
                f"/logs/{test_vehicle_id}/bulk_delete"
            )

        assert resp.status_code == 200
        assert sample_vehicle.fillups.count() == 0


def test_logs__bulk_delete_error(
    app_fixture,
    test_vehicle_id,
    test_user_id,
    sample_fillup_id_1,
    sample_fillup_ids,
    temp_vehicle_id,
    mocker,
):
    mocked_fn = mocker.MagicMock(
        "fuel_logger.fuel_logs.routes.db.session.commit", side_effect=Exception
    )
    mocker.patch("fuel_logger.fuel_logs.routes.db.session.commit", mocked_fn)

    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        sample_vehicle = db.session.get(Vehicle, test_vehicle_id)

        assert sample_vehicle.fillups.count() == 2
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.delete(
                f"/logs/{test_vehicle_id}/bulk_delete"
            )

        assert resp.status_code == 500
        assert sample_vehicle.fillups.count() == 2

        # Try with someone else's vehicle
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.delete(
                f"/logs/{temp_vehicle_id}/bulk_delete"
            )
        assert resp.status_code == 403
        assert "You have no access to these logs" in resp.text


def test_logs_bulk_upload__get(
    app_fixture,
    test_vehicle_id,
    test_user_id,
):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        sample_vehicle = db.session.get(Vehicle, test_vehicle_id)

        assert sample_vehicle.fillups.count() == 0

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(f"/logs/{test_vehicle_id}/bulk_upload")

        assert resp.status_code == 200
        assert "Upload Logs" in resp.text


def test_logs_bulk_upload__post(
    app_fixture, test_vehicle_id, test_user_id, test_username, fillups_csv
):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        sample_vehicle = db.session.get(Vehicle, test_vehicle_id)
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            test_user = db.session.get(User, test_user_id)
            sample_vehicle = db.session.get(Vehicle, test_vehicle_id)
            assert sample_vehicle.fillups.count() == 0
            resp = test_client_authenticated.post(
                f"/logs/{test_vehicle_id}/bulk_upload",
                data={"file_obj": fillups_csv},
                follow_redirects=True,
            )
            assert resp.status_code == 200
            assert f"{test_username}'s 2017 Honda (Test) Civic (Test)" in resp.text
            assert "Fuel Stats" in resp.text
            assert sample_vehicle.fillups.count() == 12

            sample_vehicle.fillups.delete()
            db.session.commit()
            assert sample_vehicle.fillups.count() == 0


def test_logs_bulk_upload__post_error(
    app_fixture, test_vehicle_id, test_user_id, invalid_csv, fillups_csv, mocker
):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        sample_vehicle = db.session.get(Vehicle, test_vehicle_id)
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            test_user = db.session.get(User, test_user_id)
            sample_vehicle = db.session.get(Vehicle, test_vehicle_id)
            assert sample_vehicle.fillups.count() == 0

            # No data
            resp = test_client_authenticated.post(
                f"/logs/{test_vehicle_id}/bulk_upload", data={}, follow_redirects=True
            )
            assert resp.status_code == 200
            assert "Upload Logs" in resp.text
            assert "No file detected" in resp.text

            # Missing columns
            resp = test_client_authenticated.post(
                f"/logs/{test_vehicle_id}/bulk_upload",
                data={"file_obj": invalid_csv},
                follow_redirects=True,
            )
            assert resp.status_code == 200
            assert "Upload Logs" in resp.text
            assert "Missing columns in CSV:" in resp.text

            # Database error (mocked)
            mocked_fn = mocker.MagicMock(
                "fuel_logger.fuel_logs.routes.db.session.commit", side_effect=Exception
            )
            mocker.patch("fuel_logger.fuel_logs.routes.db.session.commit", mocked_fn)

            resp = test_client_authenticated.post(
                f"/logs/{test_vehicle_id}/bulk_upload",
                data={"file_obj": fillups_csv},
                follow_redirects=True,
            )
            mocker.stopall()
            assert resp.status_code == 200
            assert "Upload Logs" in resp.text
            assert "Error uploading logs" in resp.text

            sample_vehicle.fillups.delete()
            db.session.commit()
            assert sample_vehicle.fillups.count() == 0


def test_logs_bulk_download(
    app_fixture, test_user_id, test_vehicle_id, sample_fillup_ids, temp_vehicle_id
):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)
        test_vehicle = db.session.get(Vehicle, test_vehicle_id)

        assert test_vehicle.fillups.count() == 2
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/logs/{test_vehicle_id}/bulk_download", follow_redirects=True
            )

        assert resp.status_code == 200
        assert resp.mimetype == "text/csv"
        assert (
            resp.headers["Content-disposition"]
            == "attachment; filename=fuel_logs_Civic (Test).csv"
        )

        df = pd.read_csv(io.StringIO(resp.data.decode()))

        assert len(df) == 2

        # Try again with someone else's data
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/logs/{temp_vehicle_id}/bulk_download", follow_redirects=True
            )

        assert resp.status_code == 403
        assert "You have no access to these logs" in resp.text


def test_logs_bulk_download__error(app_fixture, test_user_id, temp_vehicle_id):
    with app_fixture.app_context():
        test_user = db.session.get(User, test_user_id)

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                f"/logs/{temp_vehicle_id}/bulk_download", follow_redirects=True
            )

        assert resp.status_code == 403
        assert "You have no access to these logs" in resp.text
