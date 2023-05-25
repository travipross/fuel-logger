import pytest
from fuel_logger.models import User


@pytest.fixture
def test_token(app_fixture, test_user_id):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        assert user is not None

        token = user.get_api_token()

    yield token


@pytest.fixture
def test_token_header(test_token):
    return {"Authorization": f"Bearer {test_token}"}


def test_create_token(test_client, basic_auth_header, test_user_id, test_username):
    # Request a token using basic auth credentials
    resp = test_client.get("/api/tokens", headers=basic_auth_header)
    assert resp.status_code == 200
    token = resp.json.get("token")
    assert token is not None

    # Confirm token works (and is required)
    resp = test_client.get(f"/api/users/{test_user_id}")
    assert resp.status_code == 401
    assert resp.json.get("error") == "Unauthorized"

    resp = test_client.get(
        f"/api/users/{test_user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json.get("id") == test_user_id
    assert resp.json.get("username") == test_username
    assert resp.json.get("email") == "test-email@fuel-logger-flaskapp.com"


def test_revoke_token(test_client, test_token_header, test_user_id, test_username):
    # Check that token works
    resp = test_client.get(f"/api/users/{test_user_id}", headers=test_token_header)
    assert resp.status_code == 200
    assert resp.json.get("id") == test_user_id
    assert resp.json.get("username") == test_username
    assert resp.json.get("email") == "test-email@fuel-logger-flaskapp.com"

    # revoke token
    resp = test_client.delete("/api/tokens", headers=test_token_header)
    assert resp.status_code == 204
    assert resp.data == b""

    # Check that token no longer works
    resp = test_client.get(f"/api/users/{test_user_id}", headers=test_token_header)
    assert resp.status_code == 401
    assert resp.json.get("error") == "Unauthorized"
