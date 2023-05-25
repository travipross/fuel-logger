import datetime
from fuel_logger import db, KM_PER_MILE, MPG_IMP_PER_MPG, MPG_LP100K
from fuel_logger.models.users import User
from fuel_logger.models.fillups import Fillup
from fuel_logger.utils.stats import compute_stats_from_fillup_df

from datetime import datetime, timedelta
from sqlalchemy import and_

import pandas as pd


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), index=True)
    make = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer)
    is_favourite = db.Column(db.Boolean, default=False)
    odo_unit = db.Column(db.String, default="km")  # alternatively mi

    fillups = db.relationship("Fillup", backref="vehicle", lazy="dynamic")

    @property
    def current_odometer(self):
        conversion = 1 / KM_PER_MILE if self.odo_unit == "mi" else 1
        most_recent_fillup = self.fillups.order_by(Fillup.timestamp.desc()).first()
        return (
            most_recent_fillup.odometer_km * conversion if most_recent_fillup else None
        )

    def get_stats_df(self):
        df = pd.read_sql(self.fillups.statement, self.fillups.session.bind)
        df["odometer_mi"] = (df.odometer_km / KM_PER_MILE).astype(int)
        df["dist_km"] = df.odometer_km.diff()
        df["dist_mi"] = df.dist_km / KM_PER_MILE
        df["lp100k"] = df.fuel_amt_l / df.dist_km * 100
        df["mpg"] = MPG_LP100K / df.lp100k
        df["mpg_imp"] = MPG_IMP_PER_MPG * df.mpg

        return df

    def compute_stats(self):
        if len(self.fillups.all()) < 2:
            return None

        df = self.get_stats_df()
        stats = compute_stats_from_fillup_df(df)

        return stats

    def bulk_upload_logs(self, df):
        df.timestamp = df.timestamp.apply(
            lambda x: datetime.strptime(x.split(" ")[0], "%Y-%m-%d")
            + timedelta(hours=12)
        )
        f = lambda x: self.fillups.append(
            Fillup(
                timestamp=x["timestamp"],
                odometer_km=x["odometer_km"],
                fuel_amt_l=x["fuel_amt_l"],
            )
        )
        df.apply(f, axis=1)

    def __repr__(self):
        return "<Vehicle {} {}>".format(self.make, self.model)

    def to_dict(self):
        return {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "id": self.id,
        }


idx_unq_fav_vehicle = db.Index(
    "idx_unq_fav_vehicle",
    Vehicle.owner_id,
    Vehicle.is_favourite,
    sqlite_where=and_(Vehicle.is_favourite > 0),
    unique=True,
)
