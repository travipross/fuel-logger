from fuel_logger import db
from fuel_logger.api import bp
from fuel_logger.api.auth import multi_auth
from fuel_logger.models import Vehicle
from fuel_logger.schemas.vehicle import vehicle_schema, vehicles_schema

from flask import jsonify


@bp.route("/vehicles")
@multi_auth.login_required
def vehicles():
    vehicles = multi_auth.current_user().vehicles.all()

    return jsonify(vehicles_schema.dump(vehicles))


@bp.route("/vehicles/<int:id>")
@multi_auth.login_required
def vehicle_by_id(id):
    vehicle = Vehicle.query.get_or_404(id)
    return vehicle_schema.dump(vehicle)


@bp.route("/vehicles/<int:id>", methods=["DELETE"])
@multi_auth.login_required
def delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"status": "DELTETED"})
