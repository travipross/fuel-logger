from fuel_logger import db
from fuel_logger.models import Vehicle, User
from fuel_logger.vehicles import bp
from fuel_logger.vehicles.forms import VehicleForm

from flask import flash, render_template, redirect, url_for
from flask_login import login_required, current_user


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
        return redirect(url_for("vehicles.garage", user_id=current_user.id))
    return render_template("add_vehicle.html", form=form)


@bp.route("/garage/<user_id>")
@login_required
def garage(user_id):
    u = User.query.get(user_id)
    if u != current_user:
        return (
            render_template(
                "403.html", message="You don't have access to this garage."
            ),
            403,
        )
    return render_template("garage.html", user=u)


@bp.route("/set_fav_vehicle/<user_id>/<vehicle_id>")
def set_fav_vehicle(user_id, vehicle_id):
    user = User.query.get(user_id)
    vehicle = user.vehicles.filter_by(id=vehicle_id).first()
    if not user or not vehicle:
        flash("invalid user/vehicle")
    user.set_favourite_vehicle(vehicle)
    db.session.commit()
    return redirect(url_for("vehicles.garage", user_id=user_id))
