import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "maud")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGS_PER_PAGE = 5

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["no-reply@fuel-logger.herokuapp.com"]


class TestingConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "whiskey")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "test-app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGS_PER_PAGE = 5

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["no-reply@fuel-logger.herokuapp.com"]
    WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED") is not None
    PRESERVE_CONTEXT_ON_EXCEPTION = (
        False  # https://github.com/jarus/flask-testing/issues/21
    )
    TESTING = True
    SERVER_NAME = "test.app.dev"
    APPLICATION_ROOT = "/test"
    PREFERRED_URL_SCHEME = "http"
