import pytest
from fuel_logger.models import Fillup


def test_fillup_odometer_mi(app_fixture, sample_fillup_id_1):
    with app_fixture.app_context():
        sample_fillup = Fillup.query.get(sample_fillup_id_1)
    assert sample_fillup.odometer_km == 500
    assert sample_fillup.odometer_mi == 310


def test_fillup_dist(app_fixture, sample_fillup_id_1, sample_fillup_id_2):
    with app_fixture.app_context():
        sample_fillup_1 = Fillup.query.get(sample_fillup_id_1)
        sample_fillup_2 = Fillup.query.get(sample_fillup_id_2)

    assert sample_fillup_1.odometer_km == 500
    assert sample_fillup_1.dist is None

    assert sample_fillup_2.odometer_km == 1000
    assert sample_fillup_2.dist == 500


def test_fillup_dist_mi(app_fixture, sample_fillup_id_1, sample_fillup_id_2):
    with app_fixture.app_context():
        sample_fillup_1 = Fillup.query.get(sample_fillup_id_1)
        sample_fillup_2 = Fillup.query.get(sample_fillup_id_2)

    assert sample_fillup_1.dist_mi is None
    assert sample_fillup_2.dist_mi == pytest.approx(310, abs=1)


def test_fillup_lp100k(app_fixture, sample_fillup_id_1, sample_fillup_id_2):
    with app_fixture.app_context():
        sample_fillup_1 = Fillup.query.get(sample_fillup_id_1)
        sample_fillup_2 = Fillup.query.get(sample_fillup_id_2)

    assert sample_fillup_1.lp100k is None
    assert sample_fillup_2.lp100k == pytest.approx(5.0)


def test_fillup_mpg(app_fixture, sample_fillup_id_1, sample_fillup_id_2):
    with app_fixture.app_context():
        sample_fillup_1 = Fillup.query.get(sample_fillup_id_1)
        sample_fillup_2 = Fillup.query.get(sample_fillup_id_2)

    assert sample_fillup_1.mpg is None
    assert sample_fillup_2.mpg == pytest.approx(47.04, abs=0.1)


def test_fillup_mpg_imp(app_fixture, sample_fillup_id_1, sample_fillup_id_2):
    with app_fixture.app_context():
        sample_fillup_1 = Fillup.query.get(sample_fillup_id_1)
        sample_fillup_2 = Fillup.query.get(sample_fillup_id_2)

    assert sample_fillup_1.mpg_imp is None
    assert sample_fillup_2.mpg_imp == pytest.approx(56.5, abs=0.1)


def test_fillup_repr(app_fixture, sample_fillup_id_1):
    with app_fixture.app_context():
        sample_fillup_1 = Fillup.query.get(sample_fillup_id_1)

        assert (
            repr(sample_fillup_1)
            == "<Fillup date=2023-01-01 00:00:00, vehicle=testmodel1, fuel_L=50.0, odo_km=500>"
        )
