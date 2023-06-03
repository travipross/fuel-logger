import marshmallow as ma
import pytest

from fuel_logger import db
from fuel_logger.models import Vehicle
from fuel_logger.schemas.vehicle import vehicle_schema, vehicles_schema


def test_vehicle_schema__dump_one(sample_vehicle_id_1, sample_vehicle_1__serialized):
    sample_vehicle = db.session.get(Vehicle, sample_vehicle_id_1)
    assert sample_vehicle is not None
    res = vehicle_schema.dump(sample_vehicle)
    assert set(res.values()).issuperset(set(sample_vehicle_1__serialized.values()))


def test_vehicle_schema__dump_many(
    app_fixture,
    sample_vehicle_id_1,
    sample_vehicle_id_2,
    sample_vehicle_1__serialized,
    sample_vehicle_2__serialized,
):
    sample_vehicle_1 = db.session.get(Vehicle, sample_vehicle_id_1)
    sample_vehicle_2 = db.session.get(Vehicle, sample_vehicle_id_2)

    assert sample_vehicle_1 is not None
    assert sample_vehicle_2 is not None

    res = vehicles_schema.dump(
        [
            sample_vehicle_1,
            sample_vehicle_2,
        ]
    )
    for va, vb in zip(
        res, [sample_vehicle_1__serialized, sample_vehicle_2__serialized]
    ):
        assert set(va).issuperset(set(vb))


def test_vehicle_schema__dump_one_invalid():
    res = vehicle_schema.dump(123)
    assert res == {"current_odometer": None, "stats": None}


def test_vehicle_schema__dump_many_invalid():
    res = vehicles_schema.dump(
        [
            123,
            "hello",
        ]
    )
    assert res == [
        {"current_odometer": None, "stats": None},
        {"current_odometer": None, "stats": None},
    ]


def test_vehicle_schema__load_one(sample_vehicle_id_1, sample_vehicle_1__serialized):
    sample_vehicle = db.session.get(Vehicle, sample_vehicle_id_1)
    assert sample_vehicle is not None
    res = vehicle_schema.load(sample_vehicle_1__serialized)
    assert res == sample_vehicle


def test_vehicle_schema__load_many(
    app_fixture,
    sample_vehicle_id_1,
    sample_vehicle_id_2,
    sample_vehicle_1__serialized,
    sample_vehicle_2__serialized,
):
    with app_fixture.app_context():
        sample_vehicle_1 = db.session.get(Vehicle, sample_vehicle_id_1)
        sample_vehicle_2 = db.session.get(Vehicle, sample_vehicle_id_2)

        res = vehicles_schema.load(
            [sample_vehicle_1__serialized, sample_vehicle_2__serialized]
        )
        assert res == [sample_vehicle_1, sample_vehicle_2]


def test_vehicle_schema__load_one_invalid():
    with pytest.raises(ma.exceptions.ValidationError):
        vehicle_schema.load({})


def test_vehicle_schema__load_many_invalid():
    with pytest.raises(ma.exceptions.ValidationError):
        vehicles_schema.load([{}, {}])
