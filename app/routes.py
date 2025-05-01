from app import application, db
from flask import render_template, request, redirect, url_for, flash, session
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@application.route('/')
def index():
    return render_template('home.html')

@application.route('/about_us')
def about_us():
    return render_template('about_us.html')

@application.route('/profile')
def profile():
    return render_template('profile.html')

@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not (email and password):
            flash('All fields are required.', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('login'))
        
    return render_template('login.html')

@application.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if not (name and email and password and confirm_password):
            flash('All fields are required.', 'error')
            return redirect(url_for('sign_up'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('sign_up'))
        
        #check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('sign_up'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        #create new user
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Sign up successful! Please log in', 'success')
        return redirect(url_for('login'))

    return render_template('sign_up.html')

@application.route('/restaurants')
def restaurants():
    return render_template('restaurants.html')

@application.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@application.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Handle file upload
        uploaded_file = request.files.get('file')
        if uploaded_file and uploaded_file.filename.endswith('.csv'):
            flash('CSV uploaded successfully!', 'success')
        elif uploaded_file:
            flash('Only CSV files are allowed.', 'danger')

        # Handle restaurant rating
        restaurant = request.form.get('restaurant')
        rating = request.form.get('rating')
        comments = request.form.get('comments')

        if restaurant and rating:
            flash(f"Thank you for rating {restaurant}!", 'success')
        elif restaurant or rating:  # one is missing
            flash("Both restaurant name and rating are required.", 'danger')

    return render_template('upload.html')
