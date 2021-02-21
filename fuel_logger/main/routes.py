from fuel_logger import flask_app, db, KM_PER_MILE
from fuel_logger.main import bp
from fuel_logger.models import Fillup, Vehicle, User
from fuel_logger.forms import (
    VehicleForm,
    FillupForm,
    ImportForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
)
from fuel_logger.email import send_password_reset_email

from flask import render_template, redirect, url_for, flash, request, g, Response
from flask_login import login_required, current_user

import pandas as pd


@bp.route("/")
@bp.route("/index")
@login_required
def index():
    return render_template("home.html")


@bp.route("/logs/<vehicle_id>", methods=["GET", "POST"])
@login_required
def logs(vehicle_id):
    v = Vehicle.query.get_or_404(vehicle_id)
    if v.owner != current_user:
        return render_template(
            "403.html", message="You don't have access to these logs"
        )
    g.vehicle = v

    form = FillupForm()
    if form.validate_on_submit():
        odo_converted = (
            int(form.odometer.data * KM_PER_MILE)
            if v.odo_unit == "mi"
            else form.odometer.data
        )
        f = Fillup(odometer_km=odo_converted, fuel_amt_l=form.fuel.data, vehicle=v)
        db.session.add(f)
        db.session.commit()
        flash("Your fuel log has been updated!")
        return redirect(url_for("main.logs", vehicle_id=vehicle_id))

    page = request.args.get("page", 1, type=int)
    fillups = v.fillups.order_by(Fillup.timestamp.desc()).paginate(
        page, flask_app.config["LOGS_PER_PAGE"], False
    )
    next_url = (
        url_for("main.logs", vehicle_id=v.id, page=fillups.next_num)
        if fillups.has_next
        else None
    )
    prev_url = (
        url_for("main.logs", vehicle_id=v.id, page=fillups.prev_num)
        if fillups.has_prev
        else None
    )

    return render_template(
        "vehicle_logs.html",
        vehicle=v,
        form=form,
        fillups=fillups.items,
        next_url=next_url,
        prev_url=prev_url,
        page=page,
        pages=fillups.pages or 1,
    )


@bp.route("/logs/<vehicle_id>/bulk_upload", methods=["GET", "POST"])
def bulk_upload(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = ImportForm()
    if request.method == "POST":
        if "file_obj" not in request.files:
            flash("No file detected")
            return redirect(request.url)
        file = request.files["file_obj"]
        if file.filename == "":
            flash("no file selected")
            return redirect(request.url)
        if file and file.filename.endswith(".csv"):
            df = pd.read_csv(file)
            required_cols = {"timestamp", "odometer_km", "fuel_amt_l"}
            print(df.keys())
            if not set(df.keys()).issuperset(required_cols):
                missing_keys = required_cols - set(df.keys())
                flash("Missing columns in CSV: {}".format(missing_keys))
                return redirect(request.url)
            vehicle.bulk_upload_logs(df)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return redirect(url_for("logs", vehicle_id=vehicle_id))

    return render_template("upload.html", form=form)


@bp.route("/logs/<vehicle_id>/bulk_download")
def bulk_download(vehicle_id):
    v = Vehicle.query.get_or_404(vehicle_id)
    df = v.get_stats_df()
    csv = df.to_csv(
        index=False,
        columns=[
            "timestamp",
            "odometer_km",
            "fuel_amt_l",
            "dist_km",
            "lp100k",
            "mpg",
            "mpg_imp",
        ],
    )
    return Response(
        csv,
        mimetype="text/csv",
        headers={
            "Content-disposition": "attachment; filename=fuel_logs_{}.csv".format(
                v.model
            )
        },
    )


@bp.route("/logs/<vehicle_id>/bulk_delete", methods=["DELETE"])
def bulk_delete(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    for f in vehicle.fillups:
        db.session.delete(f)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash("There was a problem deleting your logs for this vehicle")
        return "", 500
    flash("All your logs have been deleted for this vehicle")
    return "", 200


@bp.route("/logs/delete/<log_id>", methods=["DELETE"])
def delete_log(log_id):
    l = Fillup.query.get_or_404(log_id)
    try:
        db.session.delete(l)
        db.session.commit()
    except:
        db.session.rollback()
        flash("There was a problem deleting this log")
        return "", 500
    flash("Your fuel log has been deleted")
    return "", 200


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
        return redirect(url_for("main.garage", user_id=current_user.id))
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
    return redirect(url_for("main.garage", user_id=user_id))
