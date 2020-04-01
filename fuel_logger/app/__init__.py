from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_bootstrap import Bootstrap

LITRE_PER_GAL = 3.785
LITRE_PER_GAL_IMP = 4.546
KM_PER_MILE = 1.609
MPG_IMP_PER_MPG = 1.2
LP100K_TO_MPG = 100*LITRE_PER_GAL/KM_PER_MILE

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
moment = Moment(app)
bootstrap = Bootstrap(app)

from app import routes, errors, models