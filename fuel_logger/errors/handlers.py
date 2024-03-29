from flask import render_template
from flask.globals import request

from fuel_logger import db
from fuel_logger.api.errors import error_response as api_error_response
from fuel_logger.errors import bp


def wants_json_response():
    return (
        request.accept_mimetypes["application/json"]
        >= request.accept_mimetypes["text/html"]
    )


@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template("404.html"), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template("500.html"), 500


@bp.app_errorhandler(403)
def forbidden_error(error):
    if wants_json_response():
        return api_error_response(403, message=str(error))
    return render_template("403.html", message=str(error)), 403
