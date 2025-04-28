from app import application
from flask import render_template

@application.route('/')
def index():
    return render_template('home.html')

@application.route('/login')
def login():
    return render_template('login.html')

@application.route('/sign_up')
def signup():
    return render_template('sign_up.html')

@application.route('/restaurants')
def restaurants():
    return render_template('restaurants.html')

if __name__ == '__main__':
    application.run()
