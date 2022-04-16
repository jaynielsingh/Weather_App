import requests
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms import *
from wtforms.validators import DataRequired, Email, Length
import os
import geocoder
from datetime import datetime, timedelta

app = Flask(__name__)
Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
OPEN_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/onecall?'
OPEN_WEATHER_ICON_URL = "http://openweathermap.org/img/wn/"
ICON_FORMAT = ".png"
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app=app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<User %r' % self.username


# db.create_all()


# TODO- Make user login database, hash the password

class RegisterForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    username = StringField(label='Username', validators=[DataRequired()])
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/location', methods=["GET", "POST"])
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

        # Daily weather information
        daily_temp = weather_data['daily'][0]['temp']
        daily_max = round(daily_temp['max'])
        daily_min = round(daily_temp['min'])

        # Hourly data for 12hrs rain
        hourly_data = weather_data['hourly'][:8]

        # Hourly Temp data
        six_hour_temp_data = weather_data['hourly'][:6]
        six_hourly_temp = [round(hour['temp']) for hour in six_hour_temp_data]

        #       Hourly Time
        current_time = datetime.now().strftime("%H")
        hour_one = datetime.now() + timedelta(hours=1)
        hour_two = datetime.now() + timedelta(hours=2)
        hour_three = datetime.now() + timedelta(hours=3)
        hour_four = datetime.now() + timedelta(hours=4)
        hour_five = datetime.now() + timedelta(hours=5)
        six_hour_time = [current_time, hour_one.strftime("%H"), hour_two.strftime("%H"), hour_three.strftime("%H"),
                         hour_four.strftime("%H"), hour_five.strftime("%H"), ]

        print(current_time, six_hour_time)

        #       Hourly Icons

        # Current hour
        current_icon_code = weather_data['hourly'][0]['weather'][0]['icon']
        current_icon = requests.get(OPEN_WEATHER_ICON_URL + current_icon_code + ICON_FORMAT).url

        # Hour 1
        hour_two_icon_code = weather_data['hourly'][1]['weather'][0]['icon']
        hour_two_icon = requests.get(OPEN_WEATHER_ICON_URL + hour_two_icon_code + ICON_FORMAT).url

        # Hour 2
        hour_three_icon_code = weather_data['hourly'][2]['weather'][0]['icon']
        hour_three_icon = requests.get(OPEN_WEATHER_ICON_URL + hour_three_icon_code + ICON_FORMAT).url

        # Hour 3
        hour_four_icon_code = weather_data['hourly'][3]['weather'][0]['icon']
        hour_four_icon = requests.get(OPEN_WEATHER_ICON_URL + hour_four_icon_code + ICON_FORMAT).url

        # Hour 4
        hour_five_icon_code = weather_data['hourly'][4]['weather'][0]['icon']
        hour_five_icon = requests.get(OPEN_WEATHER_ICON_URL + hour_five_icon_code + ICON_FORMAT).url

        # Hour 5
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

        # checking if rain is true
        will_it_rain = False
        for item in hourly_data:
            weather_id = item['weather'][0]['id']
            if weather_id < 700:
                will_it_rain = True
        if will_it_rain:
            print('Bring an umbrella')
            # TODO- Send SMS with twilio only if registered

        return render_template('result.html', current_temp=current_temp, form=form, hourly_data=hourly_data,
                               will_it_rain=will_it_rain, current_weather_main=current_weather_main,
                               current_weather_description=current_weather_description,
                               current_wind_speed=current_wind_speed, daily_min=daily_min, daily_max=daily_max,
                               current_humidity=current_humidity, current_uv_index=current_uv_index,
                               current_pressure=current_pressure, current_clouds=current_clouds,
                               six_hourly_temp=six_hourly_temp, six_hour_time=six_hour_time,
                               six_hour_icon=six_hour_icon, daily_icon=daily_icon, daily_temp=daily_temp,
                               )
    return render_template('add.html', form=form)


@app.route('/results', methods=["GET", "POST"])
def result():
    return render_template('result.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        pass
    return render_template('login.html', form=form)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            phone_number=form.phone_number.data,
            password=form.password.data
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')
    return render_template('register.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)

# TODO- Show weather data on web application.
