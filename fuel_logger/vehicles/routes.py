from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from fuel_logger import db
from fuel_logger.models import User, Vehicle
from fuel_logger.vehicles import bp
from fuel_logger.vehicles.forms import VehicleForm


@bp.route("/add_vehicle", methods=["GET", "POST"])
@login_required
def add_vehicle():
    form = VehicleForm()
    if form.validate_on_submit():
        v = Vehicle(
            make=form.make.data,
            model=form.model.data,
            year=form.year.data,
            odo_unit=form.odo_unit.data,
        )
        current_user.vehicles.append(v)
        db.session.commit()
        flash("Your vehicle has been added")
        return redirect(url_for("vehicles.garage"))
    return render_template("add_vehicle.html", form=form)


@bp.route("/garage")
@login_required
def garage():
    return render_template("garage.html")


@bp.route("/set_fav_vehicle/<vehicle_id>")
@login_required
def set_fav_vehicle(vehicle_id):
    vehicle = current_user.vehicles.filter_by(id=vehicle_id).first()
    if not vehicle:
        flash("invalid vehicle")
        return redirect(url_for("vehicles.garage"))

    current_user.set_favourite_vehicle(vehicle)
    db.session.commit()
    return redirect(url_for("vehicles.garage"))
