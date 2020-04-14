from app import app, db
from flask import render_template, redirect, url_for, flash, request, g

from app.models import Fillup, Vehicle, User
from app.forms import VehicleForm, RegistrationForm, LoginForm, FillupForm, ImportForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.exceptions import HTTPException
import pandas as pd

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
@login_required
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


@app.route("/logs/<vehicle_id>", methods=['GET', 'POST'])
@login_required
def logs(vehicle_id):
    v = Vehicle.query.get_or_404(vehicle_id)
    if v.owner != current_user:
        return render_template("403.html", message="You don't have access to these logs")
    g.vehicle = v

    form = FillupForm()
    if form.validate_on_submit():
        f = Fillup(odometer_km=form.odometer.data, fuel_amt_l=form.fuel.data, vehicle=v)
        db.session.add(f)
        db.session.commit()
        flash('Your fuel log has been updated!')
        return redirect(url_for('logs', vehicle_id=vehicle_id))
    
    page = request.args.get('page', 1, type=int)
    fillups = v.fillups.order_by(Fillup.timestamp.desc()).paginate(page, app.config['LOGS_PER_PAGE'], False)
    next_url = url_for('logs', vehicle_id=v.id, page=fillups.next_num) if fillups.has_next else None
    prev_url = url_for('logs', vehicle_id=v.id, page=fillups.prev_num) if fillups.has_prev else None

    return render_template('vehicle_logs.html', vehicle=v, form=form, fillups=fillups.items, next_url=next_url, prev_url=prev_url, page=page, pages=fillups.pages or 1)

@app.route("/logs/<vehicle_id>/bulk_upload", methods=['GET', 'POST'])
def bulk_upload(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = ImportForm()
    if request.method == "POST":
        if 'file_obj' not in request.files:
            flash("No file detected")
            return redirect(request.url)
        file = request.files['file_obj']
        if file.filename == '':
            flash("no file selected")
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            required_cols = {'timestamp', 'odometer_km', 'fuel_amt_l'}
            print(df.keys())
            if not set(df.keys()).issuperset(required_cols):
                missing_keys = required_cols - set(df.keys())
                flash("Missing columns in CSV: {}".format(missing_keys))
                return redirect(request.url)
            vehicle.bulk_upload_logs(df)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return redirect(url_for("logs", vehicle_id=vehicle_id))
    
    return render_template('upload.html', form=form)


@app.route("/logs/<vehicle_id>/bulk_delete", methods=['DELETE'])
def bulk_delete(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    for f in vehicle.fillups:
        db.session.delete(f)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash('There was a problem deleting your logs for this vehicle')
        return "", 500
    flash("All your logs have been deleted for this vehicle")
    return "", 200


@app.route("/logs/delete/<log_id>", methods=['DELETE'])
def delete_log(log_id):
    l = Fillup.query.get_or_404(log_id)
    try:
        db.session.delete(l)
        db.session.commit()
    except:
        db.session.rollback()
        flash("There was a problem deleting this log")
        return "", 500
    flash("Your fuel log has been deleted")
    return "", 200

@app.route("/add_vehicle", methods=["GET", "POST"])
@login_required
def add_vehicle():
    form = VehicleForm()
    if form.validate_on_submit():
        v = Vehicle(make=form.make.data, model=form.model.data, year=form.year.data)
        current_user.vehicles.append(v)
        db.session.commit()
        flash('Your vehicle has been added')
        return redirect(url_for('garage', user_id=current_user.id))
    return render_template('add_vehicle.html', form=form)


@app.route('/garage/<user_id>')
@login_required
def garage(user_id):
    u = User.query.get(user_id)
    if u != current_user:
        return render_template('403.html', message="You don't have access to this garage."), 403
    return render_template('garage.html', user=u)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/set_fav_vehicle/<user_id>/<vehicle_id>')
def set_fav_vehicle(user_id, vehicle_id):
    user = User.query.get(user_id)
    vehicle = user.vehicles.filter_by(id=vehicle_id).first()
    if not user or not vehicle:
        flash("invalid user/vehicle")
    user.set_favourite_vehicle(vehicle)
    db.session.commit()
    return redirect(url_for('garage', user_id=user_id))