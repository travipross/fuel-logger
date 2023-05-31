import pytest
from fuel_logger import db
from fuel_logger.models import User


@pytest.fixture
def sample_user_username():
    return "testuser-utils"


@pytest.fixture
def sample_user_email():
    return "test@user.com"


@pytest.fixture(scope="function")
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
