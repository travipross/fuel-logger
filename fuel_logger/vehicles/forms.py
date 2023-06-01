from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.fields import IntegerField
from wtforms.validators import DataRequired


class VehicleForm(FlaskForm):
    make = StringField("Vehicle Make", validators=[DataRequired()])
    model = StringField("Vehicle Model", validators=[DataRequired()])
    year = IntegerField("Vehicle Year", validators=[DataRequired()])
    odo_unit = SelectField(
        "Odometer Unit",
        validators=[DataRequired()],
        choices=[("km", "Default (km)"), ("mi", "Freedom (mi)")],
        default="km",
    )
    submit = SubmitField("Submit Vehicle")
