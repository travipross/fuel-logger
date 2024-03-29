from marshmallow import fields

from fuel_logger import ma
from fuel_logger.models import Vehicle


class VehicleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Vehicle
        load_instance = True

    id = ma.auto_field()
    make = ma.auto_field()
    model = ma.auto_field()
    year = ma.auto_field()
    odo_unit = ma.auto_field()
    is_favourite = ma.auto_field()
    current_odometer = fields.Method("get_odometer")
    stats = fields.Method("get_stats")

    def get_odometer(self, obj):
        return obj.current_odometer if hasattr(obj, "current_odometer") else None

    def get_stats(self, obj):
        return obj.compute_stats() if hasattr(obj, "compute_stats") else None


vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)
