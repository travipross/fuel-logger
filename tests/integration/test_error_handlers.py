from fuel_logger.models import User, Vehicle
from werkzeug.exceptions import InternalServerError


def test_404__html(test_client):
    resp = test_client.get(
        "/invalid_page", follow_redirects=True, headers={"Accept": "text/html"}
    )
    assert resp.status_code == 404
    assert "Not Found" in resp.text
    assert "Back" in resp.text


def test_404__json(test_client):
    resp = test_client.get(
        "/invalid_page", follow_redirects=True, headers={"Accept": "text/json"}
    )
    assert resp.status_code == 404
    assert resp.json == {"error": "Not Found"}


def test_500__html(app_fixture, test_user_id, mocker):
    mocked_fn = mocker.MagicMock(
        "fuel_logger.vehicles.forms.VehicleForm.validate_on_submit",
        side_effect=InternalServerError,
    )
    mocker.patch("fuel_logger.vehicles.forms.VehicleForm.validate_on_submit", mocked_fn)

    with app_fixture.app_context():
        test_user = User.query.get(test_user_id)
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.post(
                "/add_vehicle",
                follow_redirects=True,
                data={
                    "make": "FormTestMake",
                    "model": "FormTestModel",
                    "year": 2345,
                    "odo_unit": "km",
                },
                headers={"Accept": "text/html"},
            )

        assert resp.status_code == 500
        assert "Internal Server Error" in resp.text
        assert "Back" in resp.text


def test_500__json(app_fixture, test_user_id, mocker):
    mocked_fn = mocker.MagicMock(
        "fuel_logger.vehicles.forms.VehicleForm.validate_on_submit",
        side_effect=InternalServerError,
    )
    mocker.patch("fuel_logger.vehicles.forms.VehicleForm.validate_on_submit", mocked_fn)

    with app_fixture.app_context():
        test_user = User.query.get(test_user_id)
        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.post(
                "/add_vehicle",
                follow_redirects=True,
                data={
                    "make": "FormTestMake",
                    "model": "FormTestModel",
                    "year": 2345,
                    "odo_unit": "km",
                },
                headers={"Accept": "text/json"},
            )

        assert resp.status_code == 500
        assert resp.json == {"error": "Internal Server Error"}
