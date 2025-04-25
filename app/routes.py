from app import application
from flask import render_template

@application.route('/')
def index():
    return render_template('home.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle sign up logic here
        return redirect(url_for('index'))
    return render_template('sign_up.html')
