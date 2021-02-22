from fuel_logger.api import bp
from fuel_logger.api.auth import token_auth, basic_auth, multi_auth
from fuel_logger.models import User


from flask import jsonify


@bp.route("/users/<int:id>", methods=["GET"])
@multi_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route("/users", methods=["GET"])
@multi_auth.login_required
def get_users():
    return jsonify([u.to_dict() for u in User.query.all()])
