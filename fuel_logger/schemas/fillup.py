from fuel_logger import ma
from fuel_logger.models import Fillup, Vehicle
from fuel_logger import db

from marshmallow import fields


class FillupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Fillup
        load_instance = True

    vehicle = fields.Method("get_vehicle_description")
    vehicle_id = fields.Method("get_vehicle_id")

    def get_vehicle_id(self, obj):
        print(obj)
        vehicle = db.session.get(Vehicle, obj.vehicle_id)
        return vehicle.id if vehicle is not None else None

    def get_vehicle_description(self, obj):
        vehicle = db.session.get(Vehicle, obj.vehicle_id)
        return (
            f"{vehicle.year} {vehicle.make} {vehicle.model}"
            if vehicle is not None
            else None
        )


fillup_schema = FillupSchema()
fillups_schema = FillupSchema(many=True)
