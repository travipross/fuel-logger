from fuel_logger.utils.email import send_email, send_password_reset_email
import time
import pytest
from fuel_logger.models import User
from fuel_logger import db


def test_send_email(app_fixture, mocker):
    mock_mailer = mocker.MagicMock(name="fuel_logger.utils.email.mail")
    mocker.patch("fuel_logger.utils.email.mail", new=mock_mailer)

    with app_fixture.app_context():
        send_email(
            subject="Test",
            sender="testapp.flask@flaskapp.test.com",
            recipients=["travisprosser@gmail.com"],
            text_body="Hello world, this is a test",
            html_body="<h1>Hello world, this is a test</h1>",
        )

    time.sleep(0.05)
    mock_mailer.send.assert_called_once()
    assert mock_mailer.send.call_args.args[0].subject == "Test"
    assert (
        mock_mailer.send.call_args.args[0].sender == "testapp.flask@flaskapp.test.com"
    )
    assert mock_mailer.send.call_args.args[0].recipients == ["travisprosser@gmail.com"]
    assert mock_mailer.send.call_args.args[0].body == "Hello world, this is a test"
    assert (
        mock_mailer.send.call_args.args[0].html
        == "<h1>Hello world, this is a test</h1>"
    )


@pytest.fixture
def sample_user_username():
    return "testboi"


@pytest.fixture
def sample_user_email():
    return "test@boi.com"


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


def test_send_password_reset_email(
    app_fixture, sample_user_id, mocker, sample_user_email
):
    mock_mailer = mocker.MagicMock(name="fuel_logger.utils.email.mail")
    mocker.patch("fuel_logger.utils.email.mail", new=mock_mailer)

    with app_fixture.app_context():
        user = db.session.get(User, sample_user_id)

    send_password_reset_email(user)
    time.sleep(0.05)

    assert (
        mock_mailer.send.call_args.args[0].subject
        == "Fuel Logger - Reset Your Password"
    )
    assert mock_mailer.send.call_args.args[0].sender == app_fixture.config["ADMINS"][0]
    assert mock_mailer.send.call_args.args[0].recipients == [sample_user_email]
