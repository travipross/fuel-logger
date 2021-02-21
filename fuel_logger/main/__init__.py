from flask import Blueprint

bp = Blueprint("main", __name__)

from fuel_logger.main import routes
