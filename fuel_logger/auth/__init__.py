from flask import Blueprint

bp = Blueprint('auth', __name__)

from fuel_logger.auth import routes
