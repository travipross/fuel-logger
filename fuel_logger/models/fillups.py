from fuel_logger import db, KM_PER_MILE, MPG_IMP_PER_MPG, MPG_LP100K

from datetime import datetime

class Fillup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False, index=True)
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
