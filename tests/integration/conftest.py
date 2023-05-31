import pytest
from fuel_logger import db
from fuel_logger.models import User, Vehicle, Fillup
from requests.auth import _basic_auth_str
from datetime import datetime


@pytest.fixture(scope="session")
def test_username():
    return "test-user"


@pytest.fixture(scope="session")
def test_user_email():
    return "test-email@fuel-logger-flaskapp.com"


@pytest.fixture(scope="session")
def test_password():
    return "samplepassword"


@pytest.fixture(scope="session")
def basic_auth_header(test_username, test_password):
    return {"Authorization": _basic_auth_str(test_username, test_password)}


@pytest.fixture(scope="session")
def test_client(app_fixture):
    yield app_fixture.test_client()


@pytest.fixture(autouse=True, scope="module")
def test_vehicle_id(app_fixture):
    with app_fixture.app_context():
        vehicle = Vehicle(
            make="Honda (Test)",
            model="Civic (Test)",
            year="2017",
        )
        db.session.add(vehicle)
        db.session.commit()

        yield vehicle.id

    with app_fixture.app_context():
        db.session.delete(vehicle)
        db.session.commit()


@pytest.fixture(autouse=True, scope="module")
def test_user_id(
    test_vehicle_id, app_fixture, test_username, test_password, test_user_email
):
    with app_fixture.app_context():
        test_vehicle = Vehicle.query.get(test_vehicle_id)
        user = User(
            username=test_username,
            email=test_user_email,
            vehicles=[test_vehicle],
        )
        user.set_password(test_password)
        db.session.add(user)
        db.session.commit()

        yield user.id

    with app_fixture.app_context():
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def sample_fillup_id_1(app_fixture, test_vehicle_id):
    with app_fixture.app_context():
        fillup = Fillup(
            vehicle_id=test_vehicle_id,
            timestamp=datetime(year=2023, month=1, day=1),
            odometer_km=500,
            fuel_amt_l=50,
        )
        db.session.add(fillup)
        db.session.commit()
        yield fillup.id
        db.session.delete(fillup)
        db.session.commit()


@pytest.fixture
def sample_fillup_id_2(app_fixture, test_vehicle_id):
    with app_fixture.app_context():
        fillup = Fillup(
            vehicle_id=test_vehicle_id,
            timestamp=datetime(year=2023, month=1, day=15),
            odometer_km=1000,
            fuel_amt_l=25,
        )
        db.session.add(fillup)
        db.session.commit()
        yield fillup.id
        db.session.delete(fillup)
        db.session.commit()


@pytest.fixture
def sample_fillup_ids(sample_fillup_id_1, sample_fillup_id_2):
    yield [sample_fillup_id_1, sample_fillup_id_2]
