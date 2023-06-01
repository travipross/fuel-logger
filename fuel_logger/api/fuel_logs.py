from flask.globals import request
from fuel_logger.api import bp
from fuel_logger.api.auth import multi_auth
from fuel_logger.schemas.fillup import fillups_schema
from fuel_logger.models import Fillup
from flask import jsonify
from fuel_logger import db


@bp.route("/logs")
@multi_auth.login_required
def fuel_logs():
    if request.args.get("vehicle_id"):
        vehicle_ids = [int(request.args.get("vehicle_id"))]
    else:
        vehicle_ids = [v.id for v in multi_auth.current_user().vehicles]

    fillups = (
        db.session.execute(db.select(Fillup).filter(Fillup.vehicle_id.in_(vehicle_ids)))
        .scalars()
        .all()
    )

    return jsonify(fillups_schema.dump(fillups))
