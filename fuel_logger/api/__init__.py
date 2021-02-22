from flask import Blueprint

bp = Blueprint("api", __name__)

from fuel_logger.api import users, errors, tokens, vehicles, fuel_logs
