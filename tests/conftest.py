import pytest
import pandas as pd
import os


@pytest.fixture
def corolla_df():
    print(os.getcwd())
    return pd.read_csv(
        "tests/resources/fuel_logs_Corolla.csv", parse_dates=["timestamp"]
    )
