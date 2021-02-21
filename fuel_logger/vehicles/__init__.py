from flask import Blueprint

bp = Blueprint("vehicles", __name__)

from fuel_logger.vehicles import routes
