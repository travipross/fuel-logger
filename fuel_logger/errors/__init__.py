from flask import Blueprint

bp = Blueprint("errors", __name__)

from fuel_logger.errors import handlers
