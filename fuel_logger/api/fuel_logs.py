from flask import jsonify
from flask.globals import request

from fuel_logger import db
from fuel_logger.api import bp
from fuel_logger.api.auth import multi_auth
from fuel_logger.api.errors import bad_request, error_response
from fuel_logger.models import Fillup, Vehicle
from fuel_logger.schemas.fillup import fillup_schema, fillups_schema


@bp.route("/logs", methods=["GET", "POST"])
@multi_auth.login_required
def fuel_logs():
    vehicle_id = request.args.get("vehicle_id")

    if request.method == "GET":
        if vehicle_id:
            vehicle_ids = [int(vehicle_id)]
        else:
            vehicle_ids = [v.id for v in multi_auth.current_user().vehicles]

        fillups = (
            db.session.execute(
                db.select(Fillup).filter(Fillup.vehicle_id.in_(vehicle_ids))
            )
            .scalars()
            .all()
        )

        return jsonify(fillups_schema.dump(fillups))
    else:
        if not vehicle_id:
            return bad_request("missing vehicle_id query parameter")
        try:
            fillup = fillup_schema.load(request.json)
        except Exception as e:
            return error_response(500, str(e))

        vehicle = db.get_or_404(Vehicle, vehicle_id)
        vehicle.fillups.append(fillup)
        db.session.commit()
        return fillup_schema.dump(fillup)


@bp.route("/logs/<int:id>")
@multi_auth.login_required
def fuel_log_by_id(id):
    log = (
        db.session.execute(
            db.select(Fillup).filter_by(
                id=id
                # Fillup.vehicle.owner_id == multi_auth.current_user().id,
            )
        )
        .scalars()
        .one_or_none()
    )
    if log is not None:
        return fillup_schema.dump(log)
    else:
        return error_response(404, "No log by that ID found.")
