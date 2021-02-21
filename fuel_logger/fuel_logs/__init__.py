from flask import Blueprint

bp = Blueprint("fuel_logs", __name__)

from fuel_logger.fuel_logs import routes
