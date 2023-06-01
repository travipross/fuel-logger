from fuel_logger.api import bp
from fuel_logger.api.auth import multi_auth
from fuel_logger.models import User
from fuel_logger.schemas.user import user_schema, users_schema
from fuel_logger import db

from flask import jsonify


@bp.route("/users/<int:id>", methods=["GET"])
@multi_auth.login_required
def get_user(id):
    user = db.get_or_404(User, id)
    return user_schema.dump(user)


@bp.route("/users", methods=["GET"])
@multi_auth.login_required
def get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users))
