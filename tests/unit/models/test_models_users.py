from fuel_logger.models import User, Vehicle
from fuel_logger.models.users import load_user
from datetime import datetime, timedelta


def test_users_get_favourite_vehicle__set(
    app_fixture, sample_user_id, sample_vehicle_id_1
):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)
        assert user.vehicles.filter_by(is_favourite=True).count() == 1
        assert user.get_favourite_vehicle().id == sample_vehicle_id_1


def test_users_get_favourite_vehicle__not_set(
    app_fixture, sample_user_id, sample_vehicle_id_1
):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)
        first_vehicle = user.vehicles.first()
        sample_vehicle.is_favourite = False
        assert user.vehicles.filter_by(is_favourite=True).count() == 0

        assert user.get_favourite_vehicle().id == first_vehicle.id
        assert user.vehicles.filter_by(is_favourite=True).count() == 1


def test_users_set_favourite_vehicle(
    app_fixture, sample_user_id, sample_vehicle_id_1, sample_vehicle_id_2
):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)
        sample_vehicle_1 = Vehicle.query.get(sample_vehicle_id_1)
        sample_vehicle_2 = Vehicle.query.get(sample_vehicle_id_2)

        assert user.vehicles.filter_by(is_favourite=True).count() == 1
        assert sample_vehicle_1.is_favourite == True
        assert sample_vehicle_2.is_favourite == False

        user.set_favourite_vehicle(sample_vehicle_2)
        assert user.vehicles.filter_by(is_favourite=True).count() == 1
        assert sample_vehicle_1.is_favourite == False
        assert sample_vehicle_2.is_favourite == True


def test_load_user(app_fixture, sample_user_id):
    with app_fixture.app_context():
        loaded_user = load_user(str(sample_user_id))
        sample_user = User.query.get(sample_user_id)

        assert loaded_user.id == sample_user.id


def test_to_dict(app_fixture, sample_user_id, sample_user_username, sample_user_email):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)

        assert user.to_dict() == {
            "id": sample_user_id,
            "username": sample_user_username,
        }
        assert user.to_dict(include_email=True) == {
            "id": sample_user_id,
            "username": sample_user_username,
            "email": sample_user_email,
        }


def test_user_set_password(app_fixture, sample_user_id):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)

        assert user.password_hash is None

        user.set_password("my-test-password")

        assert user.password_hash != ""
        assert user.password_hash != "my-test-password"


def test_user_check_password(app_fixture, sample_user_id):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)

        assert user.password_hash is None

        user.set_password("another-test-password")

        assert user.password_hash != ""
        assert user.password_hash != "another-test-password"

        assert user.check_password("another-test-password") == True
        assert user.check_password(user.password_hash) == False


def test_user_repr(app_fixture, sample_user_id, sample_user_username):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)
        assert repr(user) == f"<User {sample_user_username}>"


def test_user_get_api_token(app_fixture, sample_user_id):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)

        assert user.api_token is None
        assert user.api_token_expiration is None
        token = user.get_api_token()

        # Token was created and stored
        assert user.api_token is not None

        # Token is the same after subsequent calls
        assert token == user.get_api_token()

        # New token is returned if expiration is within 60 seconds
        user.api_token_expiration = datetime.now() + timedelta(seconds=45)
        assert token != user.get_api_token()


def test_user_check_token(app_fixture, sample_user_id):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)

        assert user.api_token is None
        assert user.api_token_expiration is None

        # Returns none when token isn't found
        assert User.check_token("test") == None

        token = user.get_api_token()

        # Returns correct user based on current token
        assert User.check_token(token) == user

        # Returns None when token is expired
        user.api_token_expiration = datetime.now() - timedelta(seconds=1)
        assert User.check_token(token) == None


def test_user_revoke_token(app_fixture, sample_user_id):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)
        token = user.get_api_token()

        # Returns correct user based on current token
        assert User.check_token(token) == user

        # Returns none when token invalidated
        user.revoke_token()
        assert User.check_token(token) == None


def test_password_reset_token(app_fixture, sample_user_id):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)

        token = user.get_reset_password_token()
        assert len(token) > 0

        # confirm it's different when generated at a different time
        assert token != user.get_reset_password_token()


def test_verify_reset_password_token(app_fixture, sample_user_id):
    with app_fixture.app_context():
        user = User.query.get(sample_user_id)
        token = user.get_reset_password_token()

        # Assert the correct user was found from the token
        assert User.verify_reset_password_token(token) == user
        assert User.verify_reset_password_token("test") == None

        old_secret = app_fixture.config["SECRET_KEY"]
        app_fixture.config["SECRET_KEY"] = "new-secret-key"

        # Assert that a new secret invalidates the token and nothing is returned
        assert User.verify_reset_password_token(token) == None

        # Clean up
        app_fixture.config["SECRET_KEY"] = old_secret
