from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, BooleanField, FloatField, FileField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from app.models import User, Vehicle, Fillup
from flask import g
from sqlalchemy import func
from app import db

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
    submit = SubmitField('Submit Vehicle')


class FillupForm(FlaskForm):
    fuel = FloatField('Fuel Amount (L)', validators=[DataRequired()])
    odometer = IntegerField('Odometer Reading (km)', validators=[DataRequired()])
    submit = SubmitField('Submit Log')

    def validate_odometer(self, odometer):
        last_odo = db.session.query(func.max(Fillup.odometer_km)).scalar() or 0
        if odometer.data <= last_odo:
            raise ValidationError("Odometer value is less than a previous record.")

class ImportForm(FlaskForm):
    file_obj = FileField('Choose File', validators=[DataRequired()])
    submit = SubmitField('Begin Upload')

class DeleteAllForm(FlaskForm):
    confirm = BooleanField('Delete all logs for this vehicle?')
    submit = SubmitField('Submit')