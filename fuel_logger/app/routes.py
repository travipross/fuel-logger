from app import app 
from flask import render_template
from app.models import Fillup

@app.route("/")
@app.route("/index")
def index():
    return render_template('home.html')


@app.route('/test')
def test():
    f = Fillup.query.first()
    return render_template('_fillup.html', fillup=f)