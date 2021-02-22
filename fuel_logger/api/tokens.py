from flask.json import jsonify
from fuel_logger import db
from fuel_logger.models import User
from fuel_logger.api import bp
from fuel_logger.api.auth import basic_auth, multi_auth


@bp.route("/tokens")
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_api_token()
    db.session.commit()
    return jsonify({"token": token})


@bp.route("/tokens", methods=["DELETE"])
@multi_auth.login_required
def revoke_token():
    multi_auth.current_user().revoke_token()
    db.session.commit()
    return "", 204
