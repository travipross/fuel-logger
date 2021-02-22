from fuel_logger.api import bp
from fuel_logger.api.auth import multi_auth
from fuel_logger.models import User


@bp.route('/logs')
@multi_auth.login_required
def fuel_logs():
    return multi_auth.current_user().vehicles.to_dict()
