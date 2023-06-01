from flask import Blueprint

bp = Blueprint("api", __name__)

from fuel_logger.api import errors, fuel_logs, tokens, users, vehicles
