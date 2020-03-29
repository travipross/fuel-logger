from app import app 
from flask import render_template
from app.models import Fillup, Vehicle

@app.route("/")
@app.route("/index")
def index():
    return render_template('home.html')


@app.route("/vehicles/<vehicle_id>")
def vehicle(vehicle_id):
    v = Vehicle.query.get(vehicle_id)
    if v is None:
        return render_template('home.html')
    return render_template('vehicle.html', vehicle=v)


@app.route('/users/<username>')
def user(username):
    u = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=u)



@app.route('/test')
def test():
    f = Fillup.query.first()
    return render_template('_fillup.html', fillup=f)