from fuel_logger import ma
from fuel_logger.models import Vehicle

from marshmallow import fields

class VehicleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Vehicle
    
    id = ma.auto_field()
    make = ma.auto_field()
    model = ma.auto_field()
    year = ma.auto_field()
    odo_unit = ma.auto_field()
    current_odometer = fields.Method("get_odometer")

    def get_odometer(self, obj):
        return obj.current_odometer


vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)