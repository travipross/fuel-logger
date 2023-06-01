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


def test_register__authenticated(app_fixture, test_user_id):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        with app_fixture.test_client(user=user) as test_client_authenticated:
            # Confirm signed in
            resp = test_client_authenticated.get(
                "/auth/register", follow_redirects=True
            )
            assert resp.status_code == 200
            assert "Home page" in resp.text


def test_register__get(app_fixture, test_client):
    with app_fixture.app_context():
        resp = test_client.get("/auth/register", follow_redirects=True)
        assert resp.status_code == 200
        assert "Register" in resp.text


def test_register__new_user(app_fixture, test_client):
    with app_fixture.app_context():
        assert User.query.filter_by(username="newusername").one_or_none() is None
        resp = test_client.post(
            "/auth/register",
            follow_redirects=True,
            data={
                "username": "newusername",
                "email": "newemail@mail.com",
                "password": "newpassword",
                "password2": "newpassword",
            },
        )
        assert resp.status_code == 200
        assert "Sign In" in resp.text

        user = User.query.filter_by(username="newusername").one_or_none()
        assert user is not None

        # cleanup
        db.session.delete(user)
        db.session.commit()


def test_password_reset_request__authenticated(app_fixture, test_user_id):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        with app_fixture.test_client(user=user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                "/auth/reset_password_request", follow_redirects=True
            )

            assert resp.status_code == 200
            assert len(resp.history) == 1
            assert "Home page" in resp.text


def test_password_reset_request__get(app_fixture, test_client, test_user_email):
    with app_fixture.app_context():
        resp = test_client.get("/auth/reset_password_request", follow_redirects=True)

        assert resp.status_code == 200
        assert "Enter your email address" in resp.text


def test_password_reset_request__post(
    app_fixture, test_client, test_user_email, test_user_id, mocker
):
    mocked_fn = mocker.MagicMock("fuel_logger.auth.routes.send_password_reset_email")
    mocker.patch("fuel_logger.auth.routes.send_password_reset_email", mocked_fn)

    with app_fixture.app_context():
        resp = test_client.post(
            "/auth/reset_password_request",
            follow_redirects=True,
            data={"email": test_user_email},
        )

        assert resp.status_code == 200
        assert "Sign In" in resp.text

        assert mocked_fn.call_count == 1
        assert mocked_fn.call_args[0][0].id == test_user_id


def test_reset_password__authenticated(app_fixture, test_user_id):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        with app_fixture.test_client(user=user) as test_client_authenticated:
            resp = test_client_authenticated.get(
                "/auth/reset_password/abcd", follow_redirects=True
            )

            assert resp.status_code == 200
            assert len(resp.history) == 1
            assert "Home page" in resp.text


def test_reset_password__get_invalid(app_fixture, test_client):
    with app_fixture.app_context():
        resp = test_client.get("/auth/reset_password/abcd", follow_redirects=True)

        assert resp.status_code == 200
        assert len(resp.history) == 2
        assert "Sign In" in resp.text


def test_reset_password__post_invalid_token(
    app_fixture, test_client, test_user_id, test_password
):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        resp = test_client.post(
            "/auth/reset_password/abcd",
            follow_redirects=True,
            data={
                "password": "testpass",
                "password2": "testpass",
            },
        )

        assert resp.status_code == 200
        assert len(resp.history) == 2
        assert "Sign In" in resp.text

        assert user.check_password(test_password)
        assert not user.check_password("testpass")


def test_reset_password__post_mismatch_password(
    app_fixture, test_client, test_user_id, test_password
):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        token = user.get_reset_password_token()
        resp = test_client.post(
            f"/auth/reset_password/{token}",
            follow_redirects=True,
            data={
                "password": "testpass",
                "password2": "testpass2",
            },
        )
        assert user.check_password(test_password)
        assert not user.check_password("testpass")
        assert not user.check_password("testpass2")

        assert resp.status_code == 200
        assert "Password Reset" in resp.text


def test_reset_password__post_valid(
    app_fixture, test_client, test_user_id, test_password
):
    with app_fixture.app_context():
        user = User.query.get(test_user_id)
        token = user.get_reset_password_token()
        resp = test_client.post(
            f"/auth/reset_password/{token}",
            follow_redirects=True,
            data={
                "password": "testpass",
                "password2": "testpass",
            },
        )

        assert resp.status_code == 200
        assert len(resp.history) == 1
        assert "Sign In" in resp.text

        assert not user.check_password(test_password)
        assert user.check_password("testpass")
