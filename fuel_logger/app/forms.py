from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, BooleanField, FloatField, FileField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from wtforms.fields.html5 import DateField, TimeField
from app.models import User, Vehicle, Fillup
from flask import g
from sqlalchemy import func
from app import db, app
from datetime import datetime
from app import KM_PER_MILE


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class VehicleForm(FlaskForm):
    make = StringField('Vehicle Make', validators=[DataRequired()])
    model = StringField('Vehicle Model', validators=[DataRequired()])
    year = IntegerField('Vehicle Year', validators=[DataRequired()])
    odo_unit = SelectField('Odometer Unit', validators=[DataRequired()], choices=[('km', "Default (km)"), ('mi','Freedom (mi)')], default='km')
    submit = SubmitField('Submit Vehicle')


class FillupForm(FlaskForm):
    date = DateField('Fillup Date', default=datetime.now)
    time = TimeField("Fillup Time", default=datetime.now)
    fuel = FloatField('Fuel Amount (L)', validators=[DataRequired()])
    odometer = IntegerField('Odometer Reading (in your vehicle\'s unit)', validators=[DataRequired()])
    submit = SubmitField('Submit Log')

    def validate_odometer(self, odometer):
        last_odo = db.session.query(func.max(Fillup.odometer_km)).filter_by(vehicle_id=g.vehicle.id).scalar() or 0
        odo_val_converted = int(odometer.data*KM_PER_MILE) if g.vehicle.odo_unit == 'mi' else odometer.data
        if odo_val_converted <= last_odo:
            raise ValidationError("Odometer value is less than a previous record.")

class ImportForm(FlaskForm):
    file_obj = FileField('Choose File', validators=[DataRequired()])
    submit = SubmitField('Begin Upload')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Enter your email address', validators=[DataRequired(), Email()])
    submit = SubmitField('Send reset email')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Enter your new password', validators=[DataRequired()])
    password2 = PasswordField('Repeat your new password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')