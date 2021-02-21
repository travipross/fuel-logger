from fuel_logger import db, KM_PER_MILE
from fuel_logger.models import Fillup

from datetime import datetime
from flask import g
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import (
    DateField,
    TimeField,
    DecimalField,
    IntegerField,
    SubmitField,
    FileField,
    ValidationError,
)
from wtforms.validators import DataRequired


class FillupForm(FlaskForm):
    date = DateField("Fillup Date", default=datetime.now)
    time = TimeField("Fillup Time", default=datetime.now)
    fuel = DecimalField("Fuel Amount (L)", validators=[DataRequired()])
    odometer = IntegerField(
        "Odometer Reading (in your vehicle's unit)", validators=[DataRequired()]
    )
    submit = SubmitField("Submit Log")

    def validate_odometer(self, odometer):
        last_odo = (
            db.session.query(func.max(Fillup.odometer_km))
            .filter_by(vehicle_id=g.vehicle.id)
            .scalar()
            or 0
        )
        odo_val_converted = (
            int(odometer.data * KM_PER_MILE)
            if g.vehicle.odo_unit == "mi"
            else odometer.data
        )
        if odo_val_converted <= last_odo:
            raise ValidationError("Odometer value is less than a previous record.")


class ImportForm(FlaskForm):
    file_obj = FileField("Choose File", validators=[DataRequired()])
    submit = SubmitField("Begin Upload")
