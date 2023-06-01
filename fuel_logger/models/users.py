from fuel_logger import db, login

from flask import current_app
from flask_login import UserMixin
from time import time
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

import jwt
import base64
import os


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, index=True)
    email = db.Column(db.String)
    password_hash = db.Column(db.String(128))
    vehicles = db.relationship("Vehicle", backref="owner", lazy="dynamic")
    api_token = db.Column(db.String(32), index=True, unique=True)
    api_token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return "<User {}>".format(self.username)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return db.session.get(User, id)

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

    def get_favourite_vehicle(self):
        fav = self.vehicles.filter_by(is_favourite=True).one_or_none()
        if fav is None:
            fav = self.vehicles.first()
            self.set_favourite_vehicle(fav)
        return fav

    def get_api_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.api_token and self.api_token_expiration > now + timedelta(seconds=60):
            return self.api_token
        self.api_token = base64.b64encode(os.urandom(24)).decode("utf-8")
        self.api_token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)

        return self.api_token

    def revoke_token(self):
        self.api_token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(api_token=token).first()
        if user is None or user.api_token_expiration < datetime.utcnow():
            return None
        return user

    def to_dict(self, include_email=False):
        data = {"id": self.id, "username": self.username}

        if include_email:
            data["email"] = self.email

        return data


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
