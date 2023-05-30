import pytest
import pandas as pd
from fuel_logger.fuel_logger import create_app
from fuel_logger.config import TestingConfig
from flask_login import FlaskLoginClient


@pytest.fixture
def corolla_df():
    return pd.read_csv(
        "tests/resources/fuel_logs_Corolla.csv", parse_dates=["timestamp"]
    )


@pytest.fixture(scope="session")
def app_fixture():
    app_fixture = create_app(config_class=TestingConfig)
    app_fixture.test_client_class = FlaskLoginClient
    yield app_fixture
