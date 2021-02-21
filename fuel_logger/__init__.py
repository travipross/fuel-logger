from fuel_logger.config import Config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_mail import Mail

LITRE_PER_GAL = 3.785
LITRE_PER_GAL_IMP = 4.546
KM_PER_MILE = 1.609
MPG_IMP_PER_MPG = 1.2
MPG_LP100K = 100 * LITRE_PER_GAL / KM_PER_MILE

flask_app = Flask(__name__)
flask_app.config.from_object(Config)

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
moment = Moment()
bootstrap = Bootstrap()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    moment.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)

    from fuel_logger.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from fuel_logger.main import bp as main_bp

    app.register_blueprint(main_bp)

    from fuel_logger.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app


from fuel_logger import auth, models
