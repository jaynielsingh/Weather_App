import requests
from flask import Flask, render_template, redirect, flash, abort, url_for, request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from wtforms import *
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
import os
import geocoder
from datetime import datetime, timedelta
import pytz
from twilio.rest import Client

app = Flask(__name__)
Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
OPEN_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/onecall?'
OPEN_WEATHER_ICON_URL = "http://openweathermap.org/img/wn/"
ICON_FORMAT = ".png"
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app=app)

login_manager = LoginManager()
login_manager.init_app(app)


#   Database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(80), unique=True, nullable=False)
    phone_number = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<User %r' % self.username


# db.create_all()


#   Forms
class RegisterForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    name = StringField(label="Name", validators=[DataRequired()])
    phone_number = StringField(label="Phone Number", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Register")


class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField(label='Log In')


class LocationForm(FlaskForm):
    city = StringField("Enter your Location: ", validators=[DataRequired()])
    submit = SubmitField(label="Enter")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html', logged_in=current_user.is_authenticated)


@app.route('/location', methods=["GET", "POST"])
@login_required
def location():
    form = LocationForm()

    if form.validate_on_submit():
        data = geocoder.osm(form.city.data)
        latitude = data.lat
        longitude = data.lng
        print(latitude, longitude)
        weather_parameters = {
            "lat": latitude,
            "lon": longitude,
            "appid": WEATHER_API_KEY,
            "units": 'imperial',
        }
        response = requests.get(OPEN_WEATHER_URL, weather_parameters)
        weather_data = response.json()

        # Current weather information.
        current_temp = round(weather_data['current']['temp'])
        current_weather_description = weather_data['current']['weather'][0]['description']
        current_weather_main = weather_data['current']['weather'][0]['main']
        current_wind_speed = weather_data['current']['wind_speed']
        current_humidity = weather_data['current']['humidity']
        current_uv_index = weather_data['current']['uvi']
        current_pressure = weather_data['current']['pressure']
        current_clouds = weather_data['current']['clouds']
        current_user_dt = weather_data['current']['dt']
        current_tz = weather_data['timezone']

        # Daily weather information
        daily_temp = weather_data['daily'][0]['temp']
        daily_max = round(daily_temp['max'])
        daily_min = round(daily_temp['min'])

        # Hourly data for 8hrs rain
        hourly_data = weather_data['hourly'][:8]

        # Hourly Temp data
        six_hour_temp_data = weather_data['hourly'][:6]
        six_hourly_temp = [round(hour['temp']) for hour in six_hour_temp_data]

        #   Setting up user local time

        utc_tz = pytz.utc
        utc_dt = utc_tz.localize(datetime.utcfromtimestamp(current_user_dt))
        print(utc_dt)
        user_time = pytz.timezone(current_tz)
        local_time = utc_dt.astimezone(user_time)
        formatted_local_time = local_time.strftime("%H:" "%M")

        print(local_time)
        local_time_hour = local_time

        #       Hourly Time
        current_time = local_time_hour
        hour_one = current_time + timedelta(hours=1)
        hour_two = current_time + timedelta(hours=2)
        hour_three = current_time + timedelta(hours=3)
        hour_four = current_time + timedelta(hours=4)
        hour_five = current_time + timedelta(hours=5)
        six_hour_time = [current_time.strftime("%H"), hour_one.strftime("%H"), hour_two.strftime("%H"),
                         hour_three.strftime("%H"), hour_four.strftime("%H"), hour_five.strftime("%H"), ]

        #          Hourly Icons

        current_icon_code = weather_data['hourly'][0]['weather'][0]['icon']
        current_icon = requests.get(OPEN_WEATHER_ICON_URL + current_icon_code + ICON_FORMAT).url
        hour_two_icon_code = weather_data['hourly'][1]['weather'][0]['icon']
        hour_two_icon = requests.get(OPEN_WEATHER_ICON_URL + hour_two_icon_code + ICON_FORMAT).url
        hour_three_icon_code = weather_data['hourly'][2]['weather'][0]['icon']
        hour_three_icon = requests.get(OPEN_WEATHER_ICON_URL + hour_three_icon_code + ICON_FORMAT).url
        hour_four_icon_code = weather_data['hourly'][3]['weather'][0]['icon']
        hour_four_icon = requests.get(OPEN_WEATHER_ICON_URL + hour_four_icon_code + ICON_FORMAT).url
        hour_five_icon_code = weather_data['hourly'][4]['weather'][0]['icon']
        hour_five_icon = requests.get(OPEN_WEATHER_ICON_URL + hour_five_icon_code + ICON_FORMAT).url
        hour_six_icon_code = weather_data['hourly'][5]['weather'][0]['icon']
        hour_six_icon = requests.get(OPEN_WEATHER_ICON_URL + hour_six_icon_code + ICON_FORMAT).url
        six_hour_icon = [current_icon, hour_two_icon, hour_three_icon, hour_four_icon, hour_five_icon, hour_six_icon]

        #       Daily Weather icon and temp

        # Today
        icon_code_today = weather_data['current']['weather'][0]['icon']
        today_temp = weather_data['daily'][0]['temp']['day']
        icon_today = requests.get(OPEN_WEATHER_ICON_URL + icon_code_today + ICON_FORMAT).url

        # Tomorrow
        icon_code_tomorrow = weather_data['daily'][1]['weather'][0]['icon']
        tomorrow_temp = weather_data['daily'][1]['temp']['day']
        icon_tomorrow = requests.get(OPEN_WEATHER_ICON_URL + icon_code_tomorrow + ICON_FORMAT).url

        # Day After Tomorrow
        icon_code_dat = weather_data['daily'][2]['weather'][0]['icon']
        dat_temp = weather_data['daily'][2]['temp']['day']
        icon_dat = requests.get(OPEN_WEATHER_ICON_URL + icon_code_dat + ICON_FORMAT).url

        daily_icon = [icon_today, icon_tomorrow, icon_dat]
        daily_temp = [round(today_temp), round(tomorrow_temp), round(dat_temp)]

        print(today_temp, tomorrow_temp, dat_temp, current_weather_main)

        # Check if rain is true
        will_it_rain = False
        for item in hourly_data:
            weather_id = item['weather'][0]['id']
            if weather_id < 700:
                will_it_rain = True
        if will_it_rain:
            print('Bring an umbrella')
            client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"\nCurrent Temp: {current_temp}°F | High: {daily_max}°F | Low: {daily_min}°F | Humidity: {current_humidity}% "
                     f"It will rain in the next 8 hours, bring an ☂️ ",
                from_='+12074925019',
                to='+15104158251'
            )
            print(message.sid)
        else:
            client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"\nCurrent Temp: {current_temp}°F | High: {daily_max}°F | Low: {daily_min}°F | Humidity: {current_humidity}% "
                     f"No rain in the next 8 hours.  ",
                from_='+12074925019',
                to='+15104158251'
            )
            print(message.sid)

        return render_template('result.html', current_temp=current_temp, form=form, hourly_data=hourly_data,
                               will_it_rain=will_it_rain, current_weather_main=current_weather_main,
                               current_weather_description=current_weather_description,
                               current_wind_speed=current_wind_speed, daily_min=daily_min, daily_max=daily_max,
                               current_humidity=current_humidity, current_uv_index=current_uv_index,
                               current_pressure=current_pressure, current_clouds=current_clouds,
                               six_hourly_temp=six_hourly_temp, six_hour_time=six_hour_time,
                               six_hour_icon=six_hour_icon, daily_icon=daily_icon, daily_temp=daily_temp,
                               formatted_local_time=formatted_local_time, logged_in=current_user.is_authenticated,

                               )
    return render_template('add.html', form=form)


@app.route('/results', methods=["GET", "POST"])
@login_required
def result():
    return render_template('result.html', logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists, Try to Login')
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(
            form.password.data,
            "pbkdf2:sha256",
            16,
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            phone_number=form.phone_number.data,
            password=hashed_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    email = form.email.data
    password = form.password.data
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash("Logged in successfully")
                return redirect(url_for('index'))
            else:
                flash("Error: Incorrect password, Try Again")
                return redirect(url_for('login'))
        else:
            flash("Error: Incorrect Email, Try Again or Register")
            return redirect(url_for('login'))
    return render_template("login.html", logged_in=current_user.is_authenticated, form=form)


@app.route('/logout', methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('index'))

