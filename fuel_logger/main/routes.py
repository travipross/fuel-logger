from flask import render_template
from flask_login import login_required

from fuel_logger.main import bp


@bp.route("/")
@bp.route("/index")
@login_required
def index():
    return render_template("home.html")
