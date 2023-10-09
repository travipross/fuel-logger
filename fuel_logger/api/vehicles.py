from flask import jsonify, request

from fuel_logger import db
from fuel_logger.api import bp
from fuel_logger.api.auth import multi_auth
from fuel_logger.api.errors import bad_request, error_response
from fuel_logger.models import Vehicle
from fuel_logger.schemas.vehicle import vehicle_schema, vehicles_schema


@bp.route("/vehicles")
@multi_auth.login_required
def vehicles():
    vehicles = multi_auth.current_user().vehicles.all()

    return jsonify(vehicles_schema.dump(vehicles))


@bp.route("/vehicles/<int:id>")
@multi_auth.login_required
def vehicle_by_id(id):
    vehicle = db.get_or_404(Vehicle, id)
    return vehicle_schema.dump(vehicle)


@bp.route("/vehicles", methods=["POST"])
@multi_auth.login_required
def create_vehicle():
    data = request.get_json() or {}
    try:
        vehicle = vehicle_schema.load(data, session=db.session)
        db.session.add(vehicle)
        db.session.commit()
    except Exception as e:
        return bad_request(str(e))
    return jsonify({"status": "CREATED"})


@bp.route("/vehicles/<int:id>", methods=["DELETE"])
@multi_auth.login_required
def delete_vehicle(id):
    vehicle = db.get_or_404(Vehicle, id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"status": "DELETED"})


@bp.route("/fav_vehicle", methods=["GET", "POST"])
@multi_auth.login_required
def fav_vehicle():
    if request.method == "POST":
        id = request.get_json().get("id")
        vehicle = multi_auth.current_user().vehicles.filter_by(id=id).one_or_none()
        if vehicle:
            multi_auth.current_user().set_favourite_vehicle(vehicle)
            return jsonify({"status": "UPDATED"})
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "Vehicle can't be set as favourite as it doesn't belong to user.",
                }
            )
    vehicle = (
        multi_auth.current_user().vehicles.filter_by(is_favourite=True).one_or_none()
    )
    if vehicle:
        return vehicle_schema.dump(vehicle)
    return error_response(status_code=404, message="Vehicle not found.")
