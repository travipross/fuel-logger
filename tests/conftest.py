import pytest
import pandas as pd
import os
from fuel_logger.fuel_logger import create_app

@pytest.fixture
def corolla_df():
    print(os.getcwd())
    return pd.read_csv(
        "tests/resources/fuel_logs_Corolla.csv", parse_dates=["timestamp"]
    )

@pytest.fixture
def app_fixture():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    return create_app()

@pytest.fixture
def test_client(app_fixture):
    with app_fixture.test_client() as client:
        yield client

