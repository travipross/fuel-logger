from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class VehicleForm(FlaskForm):
    make = StringField('Vehicle Make', validators=[DataRequired()])
    model = StringField('Vehicle Model', validators=[DataRequired()])
    year = IntegerField('Vehicle Year', validators=[DataRequired()])
    submit = SubmitField('Submit Vehicle')