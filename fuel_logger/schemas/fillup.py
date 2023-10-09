from marshmallow import fields

from fuel_logger import db, ma
from fuel_logger.models import Fillup, Vehicle


class FillupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Fillup
        load_instance = True

    vehicle = fields.Method("get_vehicle_description", dump_only=True)
    vehicle_id = fields.Method("get_vehicle_id")
    dist = fields.Number(dump_only=True)
    dist_mi = fields.Number(dump_only=True)
    lp100k = fields.Number(dump_only=True)
    mpg = fields.Number(dump_only=True)
    mpg_imp = fields.Number(dump_only=True)
    odometer_mi = fields.Number(dump_only=True)

    def get_vehicle_id(self, obj):
        vehicle = (
            db.session.get(Vehicle, obj.vehicle_id)
            if hasattr(obj, "vehicle_id")
            else None
        )
        return vehicle.id if vehicle is not None else None

    def get_vehicle_description(self, obj):
        vehicle = (
            db.session.get(Vehicle, obj.vehicle_id)
            if hasattr(obj, "vehicle_id")
            else None
        )
        return (
            f"{vehicle.year} {vehicle.make} {vehicle.model}"
            if vehicle is not None
            else None
        )


fillup_schema = FillupSchema()
fillups_schema = FillupSchema(many=True)
