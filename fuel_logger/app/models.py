from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String)

    vehicles = db.relationship('Vehicle', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id))
    make = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer)

    fill_ups = db.relationship('Fillup', backref='vehicle', lazy='dynamic')

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