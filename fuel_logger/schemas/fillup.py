from fuel_logger import ma
from fuel_logger.models import Fillup, Vehicle

from marshmallow import fields


class FillupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Fillup

    vehicle = fields.Method("get_vehicle_description")
    vehicle_id = fields.Method("get_vehicle_id")

    def get_vehicle_id(self, obj):
        vehicle = Vehicle.query.get(obj.vehicle_id)
        return vehicle.id

    def get_vehicle_description(self, obj):
        vehicle = Vehicle.query.get(obj.vehicle_id)
        return f"{vehicle.year} {vehicle.make} {vehicle.model}"


fillup_schema = FillupSchema()
fillups_schema = FillupSchema(many=True)
