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
    if 'user_id' not in session:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)

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

@application.route("/restaurants")
def restaurants():
    from collections import defaultdict
    from sqlalchemy import func
    from app.models import Restaurant, Review

    # Query restaurants with their average rating
    restaurants = (
        db.session.query(Restaurant, func.avg(Review.rating).label("avg_rating"))
        .outerjoin(Review, Review.restaurant_id == Restaurant.id)
        .group_by(Restaurant.id)
        .all()
    )

    # Group by cuisine with average rating included
    grouped = defaultdict(list)
    for restaurant, avg_rating in restaurants:
        grouped[restaurant.cuisine].append((restaurant, round(avg_rating or 0, 1)))

    return render_template("restaurants.html", grouped_restaurants=grouped)

@application.route("/restaurant/<int:restaurant_id>", methods=["GET", "POST"])
def restaurant_detail(restaurant_id):
    from app.models import Restaurant, Review

    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if request.method == "POST":
        if "user_id" not in session:
            flash("You must be logged in to leave a review.", "danger")
            return redirect(url_for("login"))

        rating = int(request.form["rating"])
        date = request.form["date"]
        spend = float(request.form["spend"])
        user_id = session["user_id"]

        # Optional: prevent multiple reviews by the same user
        existing_review = Review.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
        if existing_review:
            flash("You've already submitted a review for this restaurant.", "warning")
            return redirect(url_for("restaurant_detail", restaurant_id=restaurant_id))

        review = Review(rating=rating, date=date, spend=spend, user_id=user_id, restaurant_id=restaurant_id)
        db.session.add(review)
        db.session.commit()
        flash("Thanks for your review!", "success")
        return redirect(url_for("restaurant_detail", restaurant_id=restaurant_id))

    return render_template("restaurant_detail.html", restaurant=restaurant)

@application.route("/upload_reviews", methods=["GET", "POST"])
def upload_reviews():
    if request.method == "POST":
        # Check if this is a CSV upload
        if "csv_file" in request.files:
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
                    date = row["date"]
                    spend = float(row["spend"])
                    
                    review = Review(user_id=user_id, restaurant_id=restaurant_id, rating=rating, date=date, spend=spend)
                    db.session.add(review)
                except Exception as e:
                    flash(f"Error adding review: {e}", "warning")
                    continue

            db.session.commit()
            flash("CSV uploaded successfully!", "success")
            return redirect(url_for("index"))
        
        # Handle manual rating submission
        elif "restaurant" in request.form:
            if "user_id" not in session:
                flash("You must be logged in to leave a review.", "danger")
                return redirect(url_for("login"))

            restaurant_name = request.form["restaurant"]
            rating = int(request.form["rating"])
            date = request.form["date"]
            spend = float(request.form["spend"])
            user_id = session["user_id"]
            
            # Get location and cuisine from the form
            location = request.form["location"]
            cuisine = request.form["cuisine"]

            # Check if restaurant exists, if not create it
            restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
            if not restaurant:
                restaurant = Restaurant(
                    name=restaurant_name,
                    location=location,  # Use location from the form
                    cuisine=cuisine,    # Use cuisine from the form
                    added_by=user_id
                )
                db.session.add(restaurant)
                db.session.flush()  # Get the restaurant ID without committing

            # Check for existing review
            existing_review = Review.query.filter_by(user_id=user_id, restaurant_id=restaurant.id).first()
            if existing_review:
                flash("You've already submitted a review for this restaurant.", "warning")
                return redirect(url_for("upload_reviews"))

            review = Review(rating=rating, date=date, spend=spend, user_id=user_id, restaurant_id=restaurant.id)
            db.session.add(review)
            db.session.commit()
            flash("Thanks for your review!", "success")
            return redirect(url_for("restaurants"))

    return render_template("upload_reviews.html")

@application.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))
