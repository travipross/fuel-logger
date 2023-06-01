import pytest
from fuel_logger.models import User, Vehicle, Fillup
from fuel_logger import db
from datetime import datetime
import pytest


@pytest.fixture
def sample_user_username():
    return "testboi"


@pytest.fixture
def sample_user_email():
    return "test@boi.com"


@pytest.fixture(autouse=True, scope="function")
def sample_user_id(app_fixture, sample_user_username, sample_user_email):
    with app_fixture.app_context():
        user = User(
            username=sample_user_username,
            email=sample_user_email,
        )
        db.session.add(user)
        db.session.commit()
        yield user.id
        db.session.delete(user)
        db.session.commit()


@pytest.fixture(autouse=True, scope="function")
def sample_vehicle_id_1(app_fixture, sample_user_id):
    with app_fixture.app_context():
        sample_user = db.session.get(User, sample_user_id)
        vehicle_1 = Vehicle(
            make="testmake1",
            model="testmodel1",
            year="2001",
            is_favourite=True,
            owner=sample_user,
        )
        db.session.add(vehicle_1)
        db.session.commit()
        yield vehicle_1.id
        db.session.delete(vehicle_1)
        db.session.commit()


@pytest.fixture(autouse=True, scope="function")
def sample_vehicle_id_2(app_fixture, sample_user_id):
    with app_fixture.app_context():
        sample_user = db.session.get(User, sample_user_id)
        vehicle_2 = Vehicle(
            make="testmake2",
            model="testmodel2",
            year="2002",
            is_favourite=False,
            owner=sample_user,
        )
        db.session.add(vehicle_2)
        db.session.commit()
        yield vehicle_2.id
        db.session.delete(vehicle_2)
        db.session.commit()


@pytest.fixture
def sample_fillup_id_1(app_fixture, sample_vehicle_id_1):
    with app_fixture.app_context():
        fillup = Fillup(
            vehicle_id=sample_vehicle_id_1,
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
def sample_fillup_id_2(app_fixture, sample_vehicle_id_1):
    with app_fixture.app_context():
        fillup = Fillup(
            vehicle_id=sample_vehicle_id_1,
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
