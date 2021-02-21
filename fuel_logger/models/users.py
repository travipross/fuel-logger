from fuel_logger import db, login

from flask import current_app
from flask_login import UserMixin
from time import time
from werkzeug.security import generate_password_hash, check_password_hash


import jwt


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, index=True)
    email = db.Column(db.String)
    password_hash = db.Column(db.String(128))
    vehicles = db.relationship('Vehicle', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_favourite_vehicle(self, vehicle):
        for v in self.vehicles.filter_by(is_favourite=True):
            v.is_favourite = False
        db.session.flush()
        vehicle.is_favourite = True
        db.session.commit()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
