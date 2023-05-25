import re
from flask.globals import request
from fuel_logger.models import fillups, vehicles
from fuel_logger.api import bp
from fuel_logger.api.auth import multi_auth
from fuel_logger.schemas.fillup import fillup_schema, fillups_schema
from fuel_logger.models import Fillup

from flask import jsonify


@bp.route("/logs")
@multi_auth.login_required
def fuel_logs():
    if request.args.get("vehicle_id"):
        vehicle_ids = [int(request.args.get("vehicle_id"))]
    else:
        vehicle_ids = [v.id for v in multi_auth.current_user().vehicles]
    fillups = Fillup.query.filter(Fillup.vehicle_id.in_(vehicle_ids)).all()

    return jsonify(fillups_schema.dump(fillups))
