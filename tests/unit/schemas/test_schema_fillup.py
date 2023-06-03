import marshmallow as ma
import pytest

from fuel_logger import db
from fuel_logger.models import Fillup
from fuel_logger.schemas.fillup import fillup_schema, fillups_schema


def test_fillup_schema__dump_one(sample_fillup_id_1, sample_fillup_1__serialized):
    sample_fillup = db.session.get(Fillup, sample_fillup_id_1)
    assert sample_fillup is not None
    res = fillup_schema.dump(sample_fillup)
    assert res == sample_fillup_1__serialized


def test_fillup_schema__dump_many(
    app_fixture,
    sample_fillup_id_1,
    sample_fillup_id_2,
    sample_fillup_1__serialized,
    sample_fillup_2__serialized,
):
    with app_fixture.app_context():
        sample_fillup_1 = db.session.get(Fillup, sample_fillup_id_1)
        sample_fillup_2 = db.session.get(Fillup, sample_fillup_id_2)
    assert sample_fillup_1 is not None
    assert sample_fillup_2 is not None
    res = fillups_schema.dump(
        [
            sample_fillup_1,
            sample_fillup_2,
        ]
    )
    assert res == [
        sample_fillup_1__serialized,
        sample_fillup_2__serialized,
    ]


def test_fillup_schema__dump_one_invalid():
    res = fillup_schema.dump(123)
    assert res == {"vehicle": None, "vehicle_id": None}


def test_fillup_schema__dump_many_invalid():
    res = fillups_schema.dump(
        [
            123,
            "hello",
        ]
    )
    assert res == [
        {"vehicle": None, "vehicle_id": None},
        {"vehicle": None, "vehicle_id": None},
    ]


def test_fillup_schema__load_one(sample_fillup_id_1, sample_fillup_1__serialized):
    sample_fillup = db.session.get(Fillup, sample_fillup_id_1)
    assert sample_fillup is not None
    res = fillup_schema.load(sample_fillup_1__serialized, unknown=ma.EXCLUDE)
    assert res == sample_fillup


def test_fillup_schema__load_many(
    app_fixture,
    sample_fillup_id_1,
    sample_fillup_id_2,
    sample_fillup_1__serialized,
    sample_fillup_2__serialized,
):
    with app_fixture.app_context():
        sample_fillup_1 = db.session.get(Fillup, sample_fillup_id_1)
        sample_fillup_2 = db.session.get(Fillup, sample_fillup_id_2)

        res = fillups_schema.load(
            [sample_fillup_1__serialized, sample_fillup_2__serialized],
            unknown=ma.EXCLUDE,
        )
        assert res == [sample_fillup_1, sample_fillup_2]


def test_fillup_schema__load_one_invalid():
    with pytest.raises(ma.exceptions.ValidationError):
        fillup_schema.load({})


def test_fillup_schema__load_many_invalid():
    with pytest.raises(ma.exceptions.ValidationError):
        fillups_schema.load([{}, {}])
