from app import app, db
from flask import render_template, redirect, url_for, flash, request

from app.models import Fillup, Vehicle, User
from app.forms import VehicleForm, RegistrationForm, LoginForm, FillupForm
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse


@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/vehicles/<vehicle_id>", methods=['GET', 'POST'])
def vehicle(vehicle_id):
    v = Vehicle.query.get_or_404(vehicle_id)
    form = FillupForm()
    if form.validate_on_submit():
        f = Fillup(odometer_km=form.odometer.data, fuel_amt_l=form.fuel.data, vehicle=v)
        db.session.add(f)
        db.session.commit()
        flash('Your fuel log has been updated!')
    return render_template('vehicle.html', vehicle=v, form=form)


@app.route("/add_vehicle", methods=["GET", "POST"])
def add_vehicle():
    form = VehicleForm()
    if form.validate_on_submit():
        v = Vehicle(make=form.make.data, model=form.model.data, year=form.year.data)
        current_user.vehicles.append(v)
        db.session.commit()
        flash('Your vehicle has been added')
        return redirect(url_for('user', username=current_user.username))
    return render_template('add_vehicle.html', form=form)


@app.route('/users/<username>')
def user(username):
    u = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=u)


@app.route('/test')
def test():
    f = Fillup.query.first()
    return render_template('_fillup.html', fillup=f)