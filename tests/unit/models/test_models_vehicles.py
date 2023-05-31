from fuel_logger.models import Vehicle
import pytest


def test_vehicles_get_stats_df__empty(app_fixture, sample_vehicle_id_1):
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)
        df = sample_vehicle.get_stats_df()

        assert sample_vehicle.fillups.count() == 0
        assert len(df.columns) == 11  # including id and vehicle_id
        assert len(df) == 0


def test_vehicles_get_stats_df__exception(
    app_fixture, sample_vehicle_id_1, sample_fillup_ids, mocker
):
    mocked_fn = mocker.MagicMock("pandas.read_sql", side_effect=Exception)
    mocker.patch("pandas.read_sql", mocked_fn)
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)

        # when exception is raised internally for any reason, ensure empty dataframe is returned
        df = sample_vehicle.get_stats_df()
        assert len(df.columns) == 11  # including id and vehicle_id
        assert len(df) == 0


def test_vehicles_get_stats_df__populated(
    app_fixture, sample_vehicle_id_1, sample_fillup_ids
):
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)
        df = sample_vehicle.get_stats_df()

        assert sample_vehicle.fillups.count() == 2
        assert len(df) == 2
        assert len(df.columns) == 11  # including id and vehicle_id
        assert {f.id for f in sample_vehicle.fillups.all()} == set(sample_fillup_ids)

        # note: content of these statistics are tested in test_stats.py


def test_vehicles_current_odometer__km(
    app_fixture, sample_vehicle_id_1, sample_fillup_ids
):
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)

        assert sample_vehicle.current_odometer == 1000


def test_vehicles_current_odometer__mi(
    app_fixture, sample_vehicle_id_1, sample_fillup_ids
):
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)
        sample_vehicle.odo_unit = "mi"

        assert sample_vehicle.current_odometer == pytest.approx(621.5, 0.1)


def test_vehicles_current_odometer__empty(app_fixture, sample_vehicle_id_1):
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)

        assert sample_vehicle.current_odometer == None


def test_vehicles_compute_stats__populated(
    app_fixture, sample_vehicle_id_1, sample_fillup_ids
):
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)
        stats = sample_vehicle.compute_stats()

    assert isinstance(stats, dict)
    assert len(stats) == 17


def test_vehicles_compute_stats__populated_with_one(
    app_fixture, sample_vehicle_id_1, sample_fillup_id_1
):
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)
        stats = sample_vehicle.compute_stats()

    # Can't compute stats with less than 2 fillups
    assert stats is None


def test_vehicles_repr(app_fixture, sample_vehicle_id_1):
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)

        assert repr(sample_vehicle) == f"<Vehicle testmake1 testmodel1>"


def test_vehicles_to_dict(app_fixture, sample_vehicle_id_1):
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)

    assert sample_vehicle.to_dict() == {
        "make": "testmake1",
        "model": "testmodel1",
        "year": 2001,
        "id": sample_vehicle_id_1,
    }


def test_vehicles_bulk_upload_logs(app_fixture, sample_vehicle_id_1, corolla_df):
    with app_fixture.app_context():
        sample_vehicle = Vehicle.query.get(sample_vehicle_id_1)

        assert sample_vehicle.fillups.count() == 0

        sample_vehicle.bulk_upload_logs(corolla_df)

        assert sample_vehicle.fillups.count() == len(corolla_df)
