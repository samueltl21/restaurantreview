from app import application, db
from flask import render_template, request, redirect, url_for, flash, session
from app.models import User, Restaurant, Review
from werkzeug.security import generate_password_hash, check_password_hash


@application.route('/')
def index():
    from collections import defaultdict
    from sqlalchemy import func

    # Get all restaurants and their average ratings
    restaurants = (
        db.session.query(Restaurant, func.avg(Review.rating).label("avg_rating"))
        .outerjoin(Review, Review.restaurant_id == Restaurant.id)
        .group_by(Restaurant.id)
        .all()
    )

    # Group them by cuisine
    grouped = defaultdict(list)
    for restaurant, avg_rating in restaurants:
        grouped[restaurant.cuisine].append((restaurant, round(avg_rating or 0, 1)))

    return render_template("restaurants.html", grouped_restaurants=grouped)

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

        if user and check_password_hash(user.password_hash, password):
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
        new_user = User(name=name, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Sign up successful! Please log in', 'success')
        return redirect(url_for('login'))

    return render_template('sign_up.html')

@application.route("/upload_reviews", methods=["GET", "POST"])
def upload_reviews():
    if request.method == "POST":
        file = request.files["csv_file"]
        if not file.filename.endswith(".csv"):
            flash("Only CSV files are allowed.", "danger")
            return redirect(request.url)

        import csv
        import io

        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)

        for row in reader:
            try:
                user_id = int(row["user_id"])
                restaurant_id = int(row["restaurant_id"])
                rating = int(row["rating"])
                comment = row.get("comment", "")
                
                review = Review(user_id=user_id, restaurant_id=restaurant_id, rating=rating, comment=comment)
                db.session.add(review)
            except Exception as e:
                flash(f"Error adding review: {e}", "warning")
                continue

        db.session.commit()
        flash("CSV uploaded successfully!", "success")
        return redirect(url_for("index"))

    return render_template("upload_reviews.html")

@application.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))
