from app import application
from flask import render_template, session, redirect, url_for

@application.route('/')
def index():
    return render_template('home.html')

@application.route('/profile')
def profile():
    return render_template('profile.html')
@application.route('/login')
def login():
    return render_template('login.html')

@application.route('/sign_up')
def signup():
    return render_template('sign_up.html')

if __name__ == '__main__':
    application.run()
