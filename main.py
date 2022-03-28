import requests
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import *
from wtforms.validators import DataRequired, Email, Length
import os
import geocoder

app = Flask(__name__)
Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
OPEN_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/onecall?'
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')


# TODO- Make user login database, hash the password

class RegisterForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    first_name = StringField(label='First Name', validators=[DataRequired()])
    last_name = StringField(label='Last Name', validators=[DataRequired()])
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
        }
        response = requests.get(OPEN_WEATHER_URL, weather_parameters)
        weather_data = response.json()
        hourly_data = weather_data['hourly'][:12]
        print(hourly_data)

        rain = False
        for item in hourly_data:
            weather_id = item['weather'][0]['id']
            if weather_id < 700:
                rain = True
        if rain:
            print('Bring an umbrella')
            # TODO- Send SMS with twilio only if registered
        return redirect('/')
    return render_template('add.html', form=form)


@app.route('/results', methods=["GET", "POST"])
def results():
    return render_template('results.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    return render_template('register.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)

# TODO- Show weather data on web application.


