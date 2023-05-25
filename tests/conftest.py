import pytest
import pandas as pd
import os
from fuel_logger.fuel_logger import create_app
from fuel_logger.config import TestingConfig


@pytest.fixture
def corolla_df():
    return pd.read_csv(
        "tests/resources/fuel_logs_Corolla.csv", parse_dates=["timestamp"]
    )


@pytest.fixture(scope="session")
def app_fixture():
    return create_app(config_class=TestingConfig)
