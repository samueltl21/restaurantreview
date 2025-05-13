from app import application, db
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.models import User, Restaurant, Review
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func
from app.forms import LoginForm, SignUpForm, ReviewForm
from flask_login import login_user, logout_user, current_user, login_required
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
@login_required
def profile():
    # Get the current user's reviews
    user_reviews = (
        db.session.query(Review, Restaurant)
        .join(Restaurant, Review.restaurant_id == Restaurant.id)
        .filter(Review.user_id == current_user.id)
        .all()
    )
    
    # Process data for Cuisine Preference Pie Chart
    cuisine_counts = {}
    # Process data for Average Spend per Cuisine
    cuisine_spend = {}
    cuisine_spend_count = {}
    
    for review, restaurant in user_reviews:
        # Count cuisines
        cuisine = restaurant.cuisine
        if cuisine in cuisine_counts:
            cuisine_counts[cuisine] += 1
        else:
            cuisine_counts[cuisine] = 1
            
        # Sum spend per cuisine
        if cuisine in cuisine_spend:
            cuisine_spend[cuisine] += review.spend
            cuisine_spend_count[cuisine] += 1
        else:
            cuisine_spend[cuisine] = review.spend
            cuisine_spend_count[cuisine] = 1
    
    # Calculate average spend per cuisine
    avg_spend = {}
    for cuisine in cuisine_spend:
        avg_spend[cuisine] = round(cuisine_spend[cuisine] / cuisine_spend_count[cuisine], 2)
    
    # Prepare data for charts
    cuisine_labels = list(cuisine_counts.keys())
    cuisine_values = list(cuisine_counts.values())
    
    avg_spend_labels = list(avg_spend.keys())
    avg_spend_values = list(avg_spend.values())
    
    return render_template(
        'profile.html', 
        user=current_user,
        cuisine_labels=cuisine_labels,
        cuisine_values=cuisine_values,
        avg_spend_labels=avg_spend_labels,
        avg_spend_values=avg_spend_values
    )

@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
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

        login_user(new_user)
        flash('Sign up successful! Please log in', 'success')
        return redirect(url_for('login'))

    return render_template('sign_up.html', form=form)

@application.route("/upload_reviews", methods=["GET", "POST"])
@login_required
def upload_reviews():
    form = ReviewForm()

    if form.validate_on_submit():
        # Get form data
        restaurant_name = form.restaurant.data.strip()
        location = form.location.data.strip()
        cuisine = form.cuisine.data.strip()
        rating = int(form.rating.data)
        date = form.date.data.strftime('%Y-%m-%d')
        spend = float(form.spend.data)

        # Check if restaurant exists

        restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
        if not restaurant:
            restaurant = Restaurant(
                name=restaurant_name,
                location=location,
                cuisine=cuisine,
                added_by=current_user.id
            )
            db.session.add(restaurant)
            db.session.flush()

        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            restaurant_id=restaurant.id,
            date=date
        ).first()

        if existing_review:
            flash("You've already submitted a review for this restaurant on that date", "warning")
            return redirect(url_for("upload_reviews"))

        review = Review(
            rating=rating,
            date=date,
            spend=spend,
            user_id=current_user.id,
            restaurant_id=restaurant.id
        )
        db.session.add(review)
        db.session.commit()
        flash("Thanks for your review!", "success")
        return redirect(url_for("index"))

    return render_template("upload_reviews.html", form=form)

@application.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Temp in-memory storage (use DB or Redis in production)
shared_reviews_store = {}

@application.route('/check_restaurant', methods=['POST'])
def check_restaurant():
    name = request.form.get('restaurant_name', '').strip()
    if not name:
        return jsonify({'status': 'error', 'message': 'No name provided'}), 400

    restaurant = Restaurant.query.filter_by(name=name).first()
    if restaurant:
        return jsonify({
            'status': 'exists',
            'message': 'Restaurant found!',
            'location': restaurant.location,
            'cuisine': restaurant.cuisine
        })
    else:
        return jsonify({'status': 'not_found', 'message': 'Restaurant not found.'})


@application.route('/search_restaurants', methods=['GET'])
def search_restaurants():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    matches = Restaurant.query.filter(Restaurant.name.ilike(f"%{query}%")).limit(10).all()
    return jsonify([r.name for r in matches])

@application.route('/restaurants/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    reviews = Review.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('restaurant_detail.html', restaurant=restaurant, reviews=reviews)

@application.route('/restaurants/<int:restaurant_id>/upload_image', methods=['POST'])
@login_required
def upload_restaurant_image(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if 'image' not in request.files:
        flash('No image uploaded.', 'danger')
        return redirect(url_for('restaurant_detail', restaurant_id=restaurant_id))

    file = request.files['image']
    if file.filename == '':
        flash('No selected file.', 'warning')
        return redirect(url_for('restaurant_detail', restaurant_id=restaurant_id))

    if file:
        filename = secure_filename(file.filename)
        path = os.path.join('app/static/images', filename)
        file.save(path)

        restaurant.image = filename
        db.session.commit()

        flash('Image uploaded successfully!', 'success')
        return redirect(url_for('restaurant_detail', restaurant_id=restaurant_id))


@application.route('/share_review/<int:review_id>')
def share_review(review_id):
    review = Review.query.get_or_404(review_id)
    restaurant = Restaurant.query.get_or_404(review.restaurant_id)
    user = User.query.get_or_404(review.user_id)
    return render_template('shared_reviews.html', review=review, restaurant=restaurant, user=user)
