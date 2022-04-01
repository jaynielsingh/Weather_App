import requests
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
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
        current_temp = weather_data['current']['temp']
        hourly_data = weather_data['hourly'][:12]
        rain = False
        for item in hourly_data:
            weather_id = item['weather'][0]['id']
            if weather_id < 700:
                rain = True
        if rain:
            print('Bring an umbrella')
            # TODO- Send SMS with twilio only if registered
        return render_template('result.html', current_temp=current_temp, hourly_data=hourly_data, rain=rain)
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
