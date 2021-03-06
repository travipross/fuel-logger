from app import db, login, MPG_LP100K, MPG_IMP_PER_MPG, KM_PER_MILE
from app.utils import compute_stats_from_fillup_df
from datetime import datetime, timedelta
from hashlib import md5 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import pandas as pd
from sqlalchemy import event, and_
from time import time
import jwt
from app import app

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
            app.config['SECRET_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
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

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), index=True)
    make = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer)
    is_favourite = db.Column(db.Boolean, default=False)
    odo_unit = db.Column(db.String, default='km') # alternatively mi

    fillups = db.relationship('Fillup', backref='vehicle', lazy='dynamic')

    @property
    def current_odometer(self):
        conversion = 1/KM_PER_MILE if self.odo_unit == 'mi' else 1
        return self.fillups.order_by(Fillup.timestamp.desc()).first().odometer_km * conversion


    def get_stats_df(self):
        df = pd.read_sql(self.fillups.statement, self.fillups.session.bind)
        df['odometer_mi'] = (df.odometer_km/KM_PER_MILE).astype(int)
        df['dist_km'] = df.odometer_km.diff()
        df['dist_mi'] = df.dist_km/KM_PER_MILE
        df['lp100k'] = df.fuel_amt_l/df.dist_km * 100
        df['mpg'] = MPG_LP100K / df.lp100k 
        df['mpg_imp'] = MPG_IMP_PER_MPG * df.mpg

        return df


    def compute_stats(self):
        df = self.get_stats_df()
        stats = compute_stats_from_fillup_df(df)
        
        return stats

    def bulk_upload_logs(self, df):
        df.timestamp = df.timestamp.apply(lambda x: datetime.strptime(x.split(' ')[0], '%Y-%m-%d') + timedelta(hours=12))
        f = lambda x: self.fillups.append(
            Fillup(
                    timestamp=x['timestamp'], 
                    odometer_km=x['odometer_km'], 
                    fuel_amt_l=x['fuel_amt_l']
                )
            )
        df.apply(f, axis=1)

    def __repr__(self):
        return "<Vehicle {} {}>".format(self.make, self.model)

class Fillup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey(Vehicle.id), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    odometer_km = db.Column(db.Integer, nullable=False)
    fuel_amt_l = db.Column(db.Float, nullable=False)

    @property
    def odometer_mi(self):
        return int(self.odometer_km/KM_PER_MILE)
    
    @property
    def dist(self):
        last_fillup = Fillup.query.filter_by(vehicle_id=self.vehicle_id).filter(Fillup.timestamp < self.timestamp).order_by(Fillup.timestamp.desc()).first()
        return self.odometer_km - last_fillup.odometer_km if last_fillup else None

    @property
    def dist_mi(self):
        return self.dist/KM_PER_MILE if self.dist else None

    @property
    def lp100k(self):
        return self.fuel_amt_l / self.dist * 100 if self.dist else None

    @property
    def mpg(self):
        return MPG_LP100K/self.lp100k if self.lp100k else None

    @property
    def mpg_imp(self):
        return self.mpg*MPG_IMP_PER_MPG if self.lp100k else None


    def __repr__(self):
        return "<Fillup date={}, vehicle={}, fuel_L={}, odo_km={}>".format(self.timestamp, self.vehicle.model, self.fuel_amt_l, self.odometer_km)


idx_unq_fav_vehicle = db.Index('idx_unq_fav_vehicle', Vehicle.owner_id, Vehicle.is_favourite, sqlite_where=and_(Vehicle.is_favourite > 0), unique=True)
# idx_unq_fav_vehicle = db.Index('idx_unq_fav_vehicle', Vehicle.owner_id, Vehicle.is_favourite, postgresql_where=Vehicle.is_favourite > 0, unique=True)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

