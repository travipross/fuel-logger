from app import app 
from flask import render_template, redirect, url_for, flash
from app.models import Fillup, Vehicle
from app.forms import VehicleForm

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

@app.route("/add_vehicle", methods=["GET", "POST"])
def add_vehicle():
    form = VehicleForm()
    if form.validate_on_submit():
        v = Vehicle(make=form.make.data, model=form.model.data, year=form.year.data)
        # current_user.vehicles.append(v)
        # db.session.commit()
        flash('Your vehicle has been added')
        return redirect(url_for('index'))
    return render_template('add_vehicle.html', form=form)

@app.route('/users/<username>')
def user(username):
    u = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=u)



@app.route('/test')
def test():
    f = Fillup.query.first()
    return render_template('_fillup.html', fillup=f)