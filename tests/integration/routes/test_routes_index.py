from fuel_logger.models import User


def test_index__unauthenticated(test_client):
    resp = test_client.get("/index", follow_redirects=True)
    assert "Sign In" in resp.text

    resp = test_client.get("/", follow_redirects=True)
    assert "Sign In" in resp.text


def test_index__authenticated(app_fixture, test_user_id):
    with app_fixture.app_context():
        test_user = User.query.get(test_user_id)

        with app_fixture.test_client(user=test_user) as test_client_authenticated:
            resp = test_client_authenticated.get("/index", follow_redirects=True)
            assert "Home page" in resp.text

            resp = test_client_authenticated.get("/", follow_redirects=True)
            assert "Home page" in resp.text
