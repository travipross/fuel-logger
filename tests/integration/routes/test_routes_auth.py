from fuel_logger.models import User
from fuel_logger import db
from flask_login import logout_user


def test_login_get__unauthenticated(app_fixture, test_client):
    with app_fixture.app_context():
        resp = test_client.get("/auth/login", follow_redirects=True)
        assert resp.status_code == 200
        assert "Sign In" in resp.text


def test_login_get__authenticated(app_fixture, test_user_id):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        with app_fixture.test_client(user=user) as test_client_authenticated:
            resp = test_client_authenticated.get("/auth/login", follow_redirects=True)
            assert resp.status_code == 200
            assert len(resp.history) == 1
            assert "Home page" in resp.text


def test_login_post__correct_password(
    app_fixture, test_client, test_user_id, test_password, test_username
):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        assert user.username == test_username
        assert user.check_password(test_password)
        resp = test_client.post(
            "/auth/login",
            follow_redirects=True,
            data={
                "username": test_username,
                "password": test_password,
                "remember_me": False,
            },
        )
        assert resp.status_code == 200
        assert "Home page" in resp.text

        # Check that we're now logged in
        resp = test_client.get(
            "/auth/login",
            follow_redirects=True,
            data={
                "username": test_username,
                "password": test_password,
                "remember_me": False,
            },
        )
        assert resp.status_code == 200
        assert "Home page" in resp.text


def test_login__wrong_password(
    app_fixture, test_client, test_user_id, test_password, test_username
):
    wrong_password = test_password + "s"

    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        assert user.username == test_username
        assert not user.check_password(wrong_password)
        resp = test_client.post(
            "/auth/login",
            follow_redirects=True,
            data={
                "username": test_username,
                "password": wrong_password,
                "remember_me": False,
            },
        )
        assert resp.status_code == 200
        assert len(resp.history) == 1
        assert "Sign In" in resp.text


def test_login_post__authenticated(app_fixture, test_user_id):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        with app_fixture.test_client(user=user) as test_client_authenticated:
            resp = test_client_authenticated.post("/auth/login", follow_redirects=True)
            assert resp.status_code == 200
            assert len(resp.history) == 1
            assert "Home page" in resp.text


def test_logout(app_fixture, test_user_id):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)

        with app_fixture.test_client(user=user) as test_client_authenticated:
            # Confirm signed in
            resp = test_client_authenticated.get("/index", follow_redirects=True)
            assert resp.status_code == 200
            assert "Home page" in resp.text

            # Sign out and confirm redirect
            resp = test_client_authenticated.post("/auth/logout", follow_redirects=True)

            assert resp.status_code == 200
            assert (
                len(resp.history) == 2
            )  # redirect to index, which redirects to sign-in
            assert "Sign In" in resp.text

            # confirm not signed in
            resp = test_client_authenticated.get("/index", follow_redirects=True)

            assert resp.status_code == 200
            assert len(resp.history) == 1
            assert "Sign In" in resp.text
