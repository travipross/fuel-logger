import pandas as pd
from flask import (
    Response,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.exceptions import Forbidden

from fuel_logger import KM_PER_MILE, db
from fuel_logger.fuel_logs import bp
from fuel_logger.fuel_logs.forms import FillupForm, ImportForm
from fuel_logger.models import Fillup, Vehicle


@bp.route("/logs/<vehicle_id>", methods=["GET", "POST"])
@login_required
def logs(vehicle_id):
    v = db.get_or_404(Vehicle, vehicle_id)
    if v.owner != current_user:
        raise Forbidden("You have no access to these logs")
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
        return redirect(url_for("fuel_logs.logs", vehicle_id=vehicle_id))

    page = request.args.get("page", 1, type=int)
    fillups = v.fillups.order_by(Fillup.timestamp.desc()).paginate(
        page=page, per_page=current_app.config["LOGS_PER_PAGE"], error_out=False
    )
    next_url = (
        url_for("fuel_logs.logs", vehicle_id=v.id, page=fillups.next_num)
        if fillups.has_next
        else None
    )
    prev_url = (
        url_for("fuel_logs.logs", vehicle_id=v.id, page=fillups.prev_num)
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
@login_required
def bulk_upload(vehicle_id):
    vehicle = db.get_or_404(Vehicle, vehicle_id)
    form = ImportForm()
    if request.method == "POST":
        if "file_obj" not in request.files:
            flash("No file detected")
            return redirect(request.url)
        file = request.files["file_obj"]
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
                flash("Error uploading logs")
                return redirect(request.url)
            return redirect(url_for("fuel_logs.logs", vehicle_id=vehicle_id))

    return render_template("upload.html", form=form)


@bp.route("/logs/<vehicle_id>/bulk_download")
@login_required
def bulk_download(vehicle_id):
    v = db.get_or_404(Vehicle, vehicle_id)
    if v.owner != current_user:
        raise Forbidden("You have no access to these logs")
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
@login_required
def bulk_delete(vehicle_id):
    vehicle = db.get_or_404(Vehicle, vehicle_id)
    if vehicle.owner != current_user:
        raise Forbidden("You have no access to these logs")
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
@login_required
def delete_log(log_id):
    l = db.get_or_404(Fillup, log_id)
    if l.vehicle.owner != current_user:
        raise Forbidden("You have no access to these logs")
    try:
        db.session.delete(l)
        db.session.commit()
    except:
        db.session.rollback()
        flash("There was a problem deleting this log")
        return "", 500
    flash("Your fuel log has been deleted")
    return "", 200
