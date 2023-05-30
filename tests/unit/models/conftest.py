import pytest
from fuel_logger.models import User, Vehicle
from fuel_logger import db


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
        sample_user = User.query.get(sample_user_id)
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
        sample_user = User.query.get(sample_user_id)
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
