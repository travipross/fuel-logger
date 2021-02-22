from fuel_logger import db
from fuel_logger.api import bp
from fuel_logger.api.auth import multi_auth
from fuel_logger.models import Vehicle

from flask import jsonify

@bp.route('/vehicles')
@multi_auth.login_required
def vehicles():
    return jsonify([ v.to_dict() for v in multi_auth.current_user().vehicles.all() ])

@bp.route('/vehicles/<int:id>')
@multi_auth.login_required
def vehicle_by_id(id):
    return jsonify(Vehicle.query.get_or_404(id).to_dict())

@bp.route('/vehicles/<int:id>', methods=["DELETE"])
@multi_auth.login_required
def delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify(
        {
            "status": "DELTETED"
        }
    )

