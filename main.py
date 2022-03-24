from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import *
from wtforms.validators import DataRequired, Email, Length
import os
import geopy

# TODO- Make Flask web application
app = Flask(__name__)
Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


# TODO- Make user login database, hash the password

# TODO- Make register/login form
class RegisterForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    name = StringField(label='Name', validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Log In")


class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField()


class LocationForm(FlaskForm):
    lat = StringField("Enter your Latitude: ", validators=[DataRequired()])
    lon = StringField("Enter your longitude: ", validators=[DataRequired()])
    submit = SubmitField()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/location', methods=["GET", "POST"])
def location():
    form = LocationForm()
    if form.validate_on_submit():
        lat = form.lat.data
        lon = form.lon.data
        return redirect('/')
    return render_template('add.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template('register.html')


if __name__ == "__main__":
    app.run(debug=True)

# TODO- Get current location

# TODO- Get api for weather to receive info about weather

# TODO- Show weather data on web application.

# TODO- Create login page / register page

# Only registered users can receive email with smtplib
