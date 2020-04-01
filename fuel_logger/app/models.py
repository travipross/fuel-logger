from app import db, login, LP100K_TO_MPG
from datetime import datetime
from hashlib import md5 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import pandas as pd

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    password_hash = db.Column(db.String(128))

    vehicles = db.relationship('Vehicle', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id))
    make = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer)

    fill_ups = db.relationship('Fillup', backref='vehicle', lazy='dynamic')

    @property
    def current_odometer(self):
        return self.fill_ups.order_by(Fillup.timestamp.desc()).first().odometer_km

    def __repr__(self):
        return "<Vehicle {} {}>".format(self.make, self.model)

class Fillup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey(Vehicle.id), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    odometer_km = db.Column(db.Integer, nullable=False)
    fuel_amt_l = db.Column(db.Float, nullable=False)

    @property
    def owner(self):
        return self.vehicle.owner

    def __repr__(self):
        return "<Fillup date={}, vehicle={}, fuel_L={}, dist_km={}>".format(self.timestamp, self.vehicle.model, self.fuel_amt_l, self.odometer_km)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

