import pytest
import pandas as pd
from fuel_logger.fuel_logger import create_app
from fuel_logger.config import TestingConfig
from flask_login import FlaskLoginClient
import flask_migrate


@pytest.fixture
def corolla_df():
    yield pd.read_csv(
        "tests/resources/fuel_logs_Corolla.csv", parse_dates=["timestamp"]
    )


@pytest.fixture
def fillups_csv():
    with open("tests/resources/fuel_logs_Corolla.csv", mode="rb") as file:
        yield file


@pytest.fixture
def invalid_csv():
    with open("tests/resources/fuel_logs_Corolla_invalid.csv", mode="rb") as file:
        yield file


@pytest.fixture(scope="session")
def app_fixture():
    app_fixture = create_app(config_class=TestingConfig)
    app_fixture.test_client_class = FlaskLoginClient
    yield app_fixture


@pytest.fixture(autouse=True, scope="session")
def setup_database(app_fixture):
    with app_fixture.app_context():
        flask_migrate.upgrade(directory="fuel_logger/migrations")

    yield

    with app_fixture.app_context():
        flask_migrate.downgrade(directory="fuel_logger/migrations", revision="base")
