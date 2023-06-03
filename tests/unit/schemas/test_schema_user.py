import marshmallow as ma
import pytest

from fuel_logger import db
from fuel_logger.models import User
from fuel_logger.schemas.user import user_schema, users_schema


def test_user_schema__dump_one(sample_user_id_1, sample_user_1__serialized):
    sample_user = db.session.get(User, sample_user_id_1)
    assert sample_user is not None
    res = user_schema.dump(sample_user)
    assert res == sample_user_1__serialized


def test_user_schema__dump_many(
    app_fixture,
    sample_user_id_1,
    sample_user_id_2,
    sample_user_1__serialized,
    sample_user_2__serialized,
):
    with app_fixture.app_context():
        sample_user_1 = db.session.get(User, sample_user_id_1)
        sample_user_2 = db.session.get(User, sample_user_id_2)
    assert sample_user_1 is not None
    assert sample_user_2 is not None
    res = users_schema.dump(
        [
            sample_user_1,
            sample_user_2,
        ]
    )
    assert res == [
        sample_user_1__serialized,
        sample_user_2__serialized,
    ]


def test_user_schema__dump_one_invalid():
    res = user_schema.dump(123)
    assert res == {}


def test_user_schema__dump_many_invalid():
    res = users_schema.dump(
        [
            123,
            "hello",
        ]
    )
    assert res == [{}, {}]


def test_user_schema__load_one(sample_user_id_1, sample_user_1__serialized):
    sample_user = db.session.get(User, sample_user_id_1)
    assert sample_user is not None
    res = user_schema.load(sample_user_1__serialized)
    assert res == sample_user


def test_user_schema__load_many(
    app_fixture,
    sample_user_id_1,
    sample_user_id_2,
    sample_user_1__serialized,
    sample_user_2__serialized,
):
    with app_fixture.app_context():
        sample_user_1 = db.session.get(User, sample_user_id_1)
        sample_user_2 = db.session.get(User, sample_user_id_2)

    res = users_schema.load([sample_user_1__serialized, sample_user_2__serialized])
    assert res == [sample_user_1, sample_user_2]


def test_user_schema__load_one_invalid():
    with pytest.raises(ma.exceptions.ValidationError):
        user_schema.load({})


def test_user_schema__load_many_invalid():
    with pytest.raises(ma.exceptions.ValidationError):
        users_schema.load([{}, {}])
