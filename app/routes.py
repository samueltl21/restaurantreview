from app import application
from flask import render_template, session, redirect, url_for

@application.route('/')
def index():
    return render_template('home.html')

@application.route('/profile')
def profile():
    return render_template('profile.html')