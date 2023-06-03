from datetime import datetime

import pytest

from fuel_logger import db
from fuel_logger.models import Fillup, User, Vehicle


@pytest.fixture
def sample_user_id_1(app_fixture):
    with app_fixture.app_context():
        user = User(
            username="test-user1",
            email="test-user1@testing.com",
        )
        db.session.add(user)
        db.session.commit()
        yield user.id
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def sample_user_1__serialized(sample_user_id_1):
    yield {
        "username": "test-user1",
        "email": "test-user1@testing.com",
        "id": sample_user_id_1,
    }


@pytest.fixture
def sample_user_id_2(app_fixture):
    with app_fixture.app_context():
        user = User(
            username="test-user2",
            email="test-user2@testing.com",
        )
        db.session.add(user)
        db.session.commit()

        yield user.id

        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def sample_user_2__serialized(sample_user_id_2):
    yield {
        "username": "test-user2",
        "email": "test-user2@testing.com",
        "id": sample_user_id_2,
    }


@pytest.fixture
def sample_vehicle_id_1(app_fixture):
    with app_fixture.app_context():
        vehicle = Vehicle(
            make="test-make1",
            model="test-model1",
            year=2001,
            odo_unit="km",
        )
        db.session.add(vehicle)
        db.session.commit()
        yield vehicle.id
        db.session.delete(vehicle)
        db.session.commit()


@pytest.fixture
def sample_vehicle_1__serialized(sample_vehicle_id_1):
    yield {
        "make": "test-make1",
        "model": "test-model1",
        "year": 2001,
        "odo_unit": "km",
        "id": sample_vehicle_id_1,
    }


@pytest.fixture
def sample_vehicle_id_2(app_fixture):
    with app_fixture.app_context():
        vehicle = Vehicle(
            make="test-make2",
            model="test-model2",
            year=2002,
            odo_unit="mi",
        )
        db.session.add(vehicle)
        db.session.commit()

        yield vehicle.id

        db.session.delete(vehicle)
        db.session.commit()


@pytest.fixture
def sample_vehicle_2__serialized(sample_vehicle_id_2):
    yield {
        "make": "test-make2",
        "model": "test-model2",
        "year": 2002,
        "odo_unit": "mi",
        "id": sample_vehicle_id_2,
    }


@pytest.fixture
def sample_fillup_id_1(app_fixture, sample_vehicle_id_1):
    with app_fixture.app_context():
        fillup = Fillup(
            vehicle_id=sample_vehicle_id_1,
            timestamp=datetime(year=2020, month=1, day=1, hour=12, minute=0, second=0),
            odometer_km=500,
            fuel_amt_l=25,
        )
        db.session.add(fillup)
        db.session.commit()
        yield fillup.id
        db.session.delete(fillup)
        db.session.commit()


@pytest.fixture
def sample_fillup_1__serialized(sample_fillup_id_1, sample_vehicle_id_1):
    yield {
        "id": sample_fillup_id_1,
        "timestamp": "2020-01-01T12:00:00",
        "odometer_km": 500,
        "fuel_amt_l": 25,
        "vehicle_id": sample_vehicle_id_1,
        "vehicle": "2001 test-make1 test-model1",
    }


@pytest.fixture
def sample_fillup_id_2(app_fixture, sample_vehicle_id_1):
    with app_fixture.app_context():
        fillup = Fillup(
            vehicle_id=sample_vehicle_id_1,
            timestamp=datetime(year=2020, month=1, day=2, hour=12, minute=0, second=0),
            odometer_km=1000,
            fuel_amt_l=35,
        )
        db.session.add(fillup)
        db.session.commit()

        yield fillup.id

        db.session.delete(fillup)
        db.session.commit()


@pytest.fixture
def sample_fillup_2__serialized(sample_fillup_id_2, sample_vehicle_id_1):
    yield {
        "id": sample_fillup_id_2,
        "timestamp": "2020-01-02T12:00:00",
        "odometer_km": 1000,
        "fuel_amt_l": 35,
        "vehicle_id": sample_vehicle_id_1,
        "vehicle": "2001 test-make1 test-model1",
    }
