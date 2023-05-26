from fuel_logger.utils.email import send_email
import time


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
