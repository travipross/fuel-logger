from datetime import datetime

import pytest
from requests.auth import _basic_auth_str

from fuel_logger import db
from fuel_logger.models import Fillup, User, Vehicle


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
    yield app_fixture.test_client(use_cookies=False)


@pytest.fixture(autouse=True, scope="module")
def test_vehicle_id(app_fixture):
    with app_fixture.app_context():
        vehicle = Vehicle(
            make="Honda (Test)", model="Civic (Test)", year="2017", is_favourite=True
        )
        db.session.add(vehicle)
        db.session.commit()

        yield vehicle.id

    with app_fixture.app_context():
        db.session.delete(vehicle)
        db.session.commit()


@pytest.fixture(autouse=True, scope="module")
def test_vehicle_id_alt(app_fixture):
    with app_fixture.app_context():
        vehicle = Vehicle(
            make="Honda (Test-alt)",
            model="Civic (Test-alt)",
            year="2017",
            is_favourite=False,
        )
        db.session.add(vehicle)
        db.session.commit()

        yield vehicle.id

    with app_fixture.app_context():
        db.session.delete(vehicle)
        db.session.commit()


@pytest.fixture(autouse=True, scope="module")
def test_user_id(
    test_vehicle_id,
    test_vehicle_id_alt,
    app_fixture,
    test_username,
    test_password,
    test_user_email,
):
    with app_fixture.app_context():
        test_vehicle = db.session.get(Vehicle, test_vehicle_id)
        test_vehicle_alt = db.session.get(Vehicle, test_vehicle_id_alt)
        user = User(
            username=test_username,
            email=test_user_email,
            vehicles=[test_vehicle, test_vehicle_alt],
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


@pytest.fixture(scope="function")
def secondary_vehicle_id_1(app_fixture, secondary_user_id):
    with app_fixture.app_context():
        new_user = db.session.get(User, secondary_user_id)
        new_vehicle_1 = Vehicle(
            make="make1",
            model="model1",
            year="2001",
            is_favourite=True,
            owner=new_user,
        )
        db.session.add(new_vehicle_1)
        db.session.commit()
        yield new_vehicle_1.id
        db.session.delete(new_vehicle_1)
        db.session.commit()


@pytest.fixture(scope="function")
def secondary_vehicle_id_2(app_fixture, secondary_user_id):
    with app_fixture.app_context():
        new_user = db.session.get(User, secondary_user_id)
        new_vehicle_2 = Vehicle(
            make="make2",
            model="model2",
            year="2002",
            is_favourite=False,
            owner=new_user,
        )
        db.session.add(new_vehicle_2)
        db.session.commit()
        yield new_vehicle_2.id
        db.session.delete(new_vehicle_2)
        db.session.commit()


@pytest.fixture(scope="function")
def secondary_user_id(app_fixture):
    with app_fixture.app_context():
        new_user = User(
            username="secondary_user",
            email="doesntmatter@ignore.com",
        )
        db.session.add(new_user)
        db.session.commit()
        new_user_id = new_user.id
        yield new_user_id
        db.session.delete(new_user)
        db.session.commit()


@pytest.fixture
def secondary_vehicle_id(app_fixture, test_user_id):
    v = Vehicle(
        make="MadeUpMake",
        model="MadeUpModel",
        year="1234",
    )
    with app_fixture.app_context():
        user = db.session.get(User, test_user_id)
        user.vehicles.append(v)
        db.session.flush()
        assert v.is_favourite == False
        db.session.commit()
        yield v.id
        db.session.delete(v)
        db.session.commit()
