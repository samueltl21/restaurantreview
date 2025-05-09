from app import application, db
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.models import User, Restaurant, Review
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from app.forms import LoginForm, SignUpForm
import uuid

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

    # Top 3 restaurants by average rating
    sorted_by_rating = sorted(restaurants, key=lambda x: x[1] or 0, reverse=True)
    top_restaurants = sorted_by_rating[:3]

    # Group them by cuisine
    grouped = defaultdict(list)
    for restaurant, avg_rating in restaurants:
        grouped[restaurant.cuisine].append((restaurant, round(avg_rating or 0, 1)))

    return render_template("restaurants.html", grouped_restaurants=grouped, top_restaurants=top_restaurants)

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
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'danger')
    return render_template('login.html', form=form)

@application.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('sign_up'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Sign up successful! Please log in', 'success')
        return redirect(url_for('login'))

    return render_template('sign_up.html', form=form)

@application.route("/upload_reviews", methods=["GET", "POST"])
def upload_reviews():
    if request.method == "POST":
        # --- CSV Upload ---
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
                    email = row["email"].strip()
                    user = User.query.filter_by(email=email).first()
                    if not user:
                        flash(f"User with email {email} not found. Skipping row.", "warning")
                        continue

                    restaurant_name = row["restaurant_name"].strip()
                    rating = int(row["rating"])
                    date = row["date"].strip()
                    spend = float(row["spend"])
                    location = row["location"].strip()
                    cuisine = row["cuisine"].strip()

                    # Check or create restaurant
                    restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
                    if not restaurant:
                        restaurant = Restaurant(
                            name=restaurant_name,
                            location=location,
                            cuisine=cuisine,
                            added_by=user.id
                        )
                        db.session.add(restaurant)
                        db.session.flush()

                    # Skip if review already exists
                    existing_review = Review.query.filter_by(user_id=user.id, restaurant_id=restaurant.id).first()
                    if existing_review:
                        flash(f"Duplicate review skipped for '{restaurant_name}' by {email}", "warning")
                        continue

                    review = Review(
                        user_id=user.id,
                        restaurant_id=restaurant.id,
                        rating=rating,
                        date=date,
                        spend=spend
                    )
                    db.session.add(review)

                except Exception as e:
                    flash(f"Error processing row for email {row.get('email', 'unknown')}: {e}", "danger")
                    continue

            db.session.commit()
            flash("CSV uploaded and processed successfully!", "success")
            return redirect(url_for("index"))

        # --- Manual Form Submission ---
        elif "restaurant" in request.form:
            if "user_id" not in session:
                flash("You must be logged in to leave a review.", "danger")
                return redirect(url_for("login"))

            restaurant_name = request.form["restaurant"]
            rating = int(request.form["rating"])
            date = request.form["date"]
            spend = float(request.form["spend"])
            user_id = session["user_id"]
            location = request.form["location"]
            cuisine = request.form["cuisine"]

            restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
            if not restaurant:
                restaurant = Restaurant(
                    name=restaurant_name,
                    location=location,
                    cuisine=cuisine,
                    added_by=user_id
                )
                db.session.add(restaurant)
                db.session.flush()

            existing_review = Review.query.filter_by(user_id=user_id, restaurant_id=restaurant.id).first()
            if existing_review:
                flash("You've already submitted a review for this restaurant.", "warning")
                return redirect(url_for("upload_reviews"))

            review = Review(
                rating=rating,
                date=date,
                spend=spend,
                user_id=user_id,
                restaurant_id=restaurant.id
            )
            db.session.add(review)
            db.session.commit()
            flash("Thanks for your review!", "success")
            return redirect(url_for("index"))

    return render_template("upload_reviews.html")

@application.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@application.route("/analytics")
def analytics():
    top_restaurants = (
        db.session.query(Restaurant.name, func.count(Review.id).label("review_count"))
        .join(Review)
        .group_by(Restaurant.id)
        .order_by(func.count(Review.id).desc())
        .limit(3)
        .all()
    )

    labels = [r[0] for r in top_restaurants]
    values = [r[1] for r in top_restaurants]

    return render_template("analytics.html", labels=labels, values=values)

# Temp in-memory storage (use DB or Redis in production)
shared_reviews_store = {}

@application.route('/generate_share_link', methods=['POST'])
def generate_share_link():
    data = request.get_json()
    review_ids = data.get('review_ids', [])

    # Generate a unique token
    token = str(uuid.uuid4())

    # Optional: validate review_ids from DB
    shared_reviews_store[token] = review_ids  # store for retrieval later

    return jsonify({"token": token})

@application.route('/shared/<token>')
def view_shared_reviews(token):
    review_ids = shared_reviews_store.get(token)
    if not review_ids:
        return "Invalid or expired link", 404

    # Get the reviews
    reviews = Review.query.filter(Review.id.in_(review_ids)).all()

    return render_template("shared_reviews.html", reviews=reviews)