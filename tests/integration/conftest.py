import pytest
from fuel_logger import db
import flask_migrate
from fuel_logger.models import User, Vehicle
from requests.auth import _basic_auth_str


@pytest.fixture(scope="session")
def test_username():
    return "test-user"


@pytest.fixture(scope="session")
def test_user_email():
    return "test-email@fuel-logger-flaskapp.com"


@pytest.fixture(scope="session")
def test_password():
    return "samplepassword"


@pytest.fixture
def basic_auth_header(test_username, test_password):
    return {"Authorization": _basic_auth_str(test_username, test_password)}


@pytest.fixture(autouse=True, scope="session")
def setup_database(app_fixture):
    with app_fixture.app_context():
        flask_migrate.upgrade(directory="fuel_logger/migrations")
        yield

    with app_fixture.app_context():
        flask_migrate.downgrade(directory="fuel_logger/migrations", revision="base")


@pytest.fixture()
def test_client(app_fixture):
    yield app_fixture.test_client()


@pytest.fixture(autouse=True, scope="session")
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


@pytest.fixture(autouse=True, scope="session")
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
