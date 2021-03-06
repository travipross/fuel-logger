from flask import Flask
from config import Config
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
MPG_LP100K = 100*LITRE_PER_GAL/KM_PER_MILE

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
moment = Moment(app)
bootstrap = Bootstrap(app)
mail = Mail(app)

from app import routes, errors, models