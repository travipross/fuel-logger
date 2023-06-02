import pytest

from fuel_logger import db
from fuel_logger.models import User


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
