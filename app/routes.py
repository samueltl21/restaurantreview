from app import application, db
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.models import User, Restaurant, Review, SharedReview, SharedComment, SharedReviewEntry
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func, asc
from app.forms import LoginForm, SignUpForm, ReviewForm
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
import os
import uuid
import json

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
    # Get all reviews from the current user
    user_reviews = Review.query.filter_by(user_id=current_user.id).all()

    # Initialize dictionaries for chart data
    cuisine_counts = {}
    cuisine_spend = {}
    cuisine_spend_count = {}

    total_rating = 0
    total_spend = 0
    num_reviews = len(user_reviews)

    for review in user_reviews:
        if review.restaurant:  # Ensure restaurant relationship is loaded
            cuisine = review.restaurant.cuisine

            # Count for cuisine chart
            cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1

            # Sum for avg spend per cuisine
            cuisine_spend[cuisine] = cuisine_spend.get(cuisine, 0) + review.spend
            cuisine_spend_count[cuisine] = cuisine_spend_count.get(cuisine, 0) + 1

            # Sum for overall stats
            total_rating += review.rating
            total_spend += review.spend

    # Calculate average spend per cuisine
    avg_spend_by_cuisine = {
        cuisine: round(cuisine_spend[cuisine] / cuisine_spend_count[cuisine], 2)
        for cuisine in cuisine_spend
    }

    # Prepare data for charts
    cuisine_labels = list(cuisine_counts.keys())
    cuisine_values = list(cuisine_counts.values())

    avg_spend_labels = list(avg_spend_by_cuisine.keys())
    avg_spend_values = list(avg_spend_by_cuisine.values())

    # Compute overall averages
    avg_rating = round(total_rating / num_reviews, 1) if num_reviews > 0 else 0
    avg_spend = round(total_spend / num_reviews, 2) if num_reviews > 0 else 0

    # Get other users for sharing dropdown
    all_users = User.query.filter(User.id != current_user.id).all()

    return render_template(
        'profile.html',
        user=current_user,
        cuisine_labels=cuisine_labels,
        cuisine_values=cuisine_values,
        avg_spend_labels=avg_spend_labels,
        avg_spend_values=avg_spend_values,
        avg_rating=avg_rating,
        avg_spend=avg_spend,
        all_users=all_users
    )


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

@application.route("/share_reviews", methods=["POST"])
@login_required
def share_reviews():
    data = request.get_json()
    review_ids = data.get("review_ids")
    recipient_id = data.get("recipient_id")

    if not review_ids or not recipient_id:
        return jsonify({"success": False, "message": "Missing data"}), 400

    recipient = User.query.get(recipient_id)
    if not recipient:
        return jsonify({"success": False, "message": "Recipient not found"}), 404

    # Ensure unique review IDs
    review_ids = list(set(review_ids))

    existing_thread = SharedReview.query.filter(
        ((SharedReview.sender_id == current_user.id) & (SharedReview.recipient_id == recipient_id)) |
        ((SharedReview.sender_id == recipient_id) & (SharedReview.recipient_id == current_user.id))
    ).first()

    if existing_thread:
        existing_ids = json.loads(existing_thread.review_ids)
        new_ids = [rid for rid in review_ids if rid not in existing_ids]
        if not new_ids:
            return jsonify({"success": True, "url": url_for("view_shared_conversation", user_id=recipient_id)})

        # Update review ID list
        combined_ids = existing_ids + new_ids
        existing_thread.review_ids = json.dumps(combined_ids)

        for review_id in new_ids:
            # 🛡️ Extra safety check to avoid duplication
            already_exists = SharedReviewEntry.query.filter_by(
                shared_review_id=existing_thread.id,
                review_id=review_id
            ).first()
            if not already_exists:
                entry = SharedReviewEntry(
                    shared_review_id=existing_thread.id,
                    review_id=review_id,
                    shared_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                db.session.add(entry)

        db.session.commit()
        return jsonify({"success": True, "url": url_for("view_shared_conversation", user_id=recipient_id)})

    else:
        token = str(uuid.uuid4())
        shared = SharedReview(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            token=token,
            review_ids=json.dumps(review_ids),
            shared_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        db.session.add(shared)
        db.session.flush()  # Get shared.id

        for review_id in review_ids:
            entry = SharedReviewEntry(
                shared_review_id=shared.id,
                review_id=review_id,
                shared_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            db.session.add(entry)

        db.session.commit()
        return jsonify({"success": True, "url": url_for("view_shared_conversation", user_id=recipient_id)})

@application.route('/shared/<token>', methods=["GET", "POST"])
@login_required
def view_shared_reviews(token):
    shared = SharedReview.query.filter_by(token=token).first_or_404()

    if current_user.id not in [shared.sender_id, shared.recipient_id]:
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        content = request.form.get("comment", "").strip()
        if content:
            new_comment = SharedComment(
                shared_review_id=shared.id,
                user_id=current_user.id,
                content=content,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("view_shared_reviews", token=token))

    review_ids = json.loads(shared.review_ids)
    reviews = Review.query.filter(Review.id.in_(review_ids)).all()
    sender = User.query.get(shared.sender_id)
    recipient = User.query.get(shared.recipient_id)
    comments = SharedComment.query.filter_by(shared_review_id=shared.id).order_by(SharedComment.timestamp).all()

    return render_template("shared_reviews.html", reviews=reviews, sender=sender, recipient=recipient, comments=comments)

@application.route('/shared/conversation/<int:user_id>', methods=["GET", "POST"])
@login_required
def view_shared_conversation(user_id):
    other_user = User.query.get_or_404(user_id)

    if other_user.id == current_user.id:
        flash("Cannot view a conversation with yourself.", "warning")
        return redirect(url_for("profile"))

    # Get all threads between the current user and the other user
    shared_threads = SharedReview.query.filter(
        ((SharedReview.sender_id == current_user.id) & (SharedReview.recipient_id == other_user.id)) |
        ((SharedReview.sender_id == other_user.id) & (SharedReview.recipient_id == current_user.id))
    ).all()

    if not shared_threads:
        flash("No shared history found with this user.", "info")
        return redirect(url_for("shared_with"))

    shared_thread_ids = [thread.id for thread in shared_threads]

    # Get all SharedReviewEntry rows (review_id, shared_at) for the threads
    entry_data = (
        db.session.query(SharedReviewEntry, Review, SharedReview, User)
        .join(Review, SharedReviewEntry.review_id == Review.id)
        .join(SharedReview, SharedReviewEntry.shared_review_id == SharedReview.id)
        .join(User, SharedReview.sender_id == User.id)
        .filter(SharedReviewEntry.shared_review_id.in_(shared_thread_ids))
        .all()
    )

    timeline = []

    for entry, review, thread, sender in entry_data:
        timeline.append({
            "type": "review",
            "timestamp": entry.shared_at,
            "data": review,
            "sender": sender
        })

    # Get all comments on those threads
    comments = SharedComment.query.filter(
        SharedComment.shared_review_id.in_(shared_thread_ids)
    ).order_by(SharedComment.timestamp).all()

    for comment in comments:
        timeline.append({
            "type": "comment",
            "timestamp": comment.timestamp,
            "data": comment,
            "sender": comment.user
        })

    # Sort everything by timestamp (ascending)
    timeline.sort(key=lambda x: x["timestamp"])

    # Handle new comment POST
    if request.method == "POST":
        content = request.form.get("comment", "").strip()
        if content:
            # Assign the comment to the first thread
            comment = SharedComment(
                shared_review_id=shared_threads[0].id,
                user_id=current_user.id,
                content=content,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for("view_shared_conversation", user_id=other_user.id))

    return render_template("shared_conversation.html", other_user=other_user, items=timeline)

@application.route('/shared_with')
@login_required
def shared_with():
    threads = SharedReview.query.filter(
        (SharedReview.sender_id == current_user.id) | 
        (SharedReview.recipient_id == current_user.id)
    ).all()

    user_ids = set()
    for thread in threads:
        user_ids.add(thread.sender_id if thread.sender_id != current_user.id else thread.recipient_id)

    users = User.query.filter(User.id.in_(user_ids)).all()
    return render_template("shared_with.html", shared_users=users)

@application.route('/search_users', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    matches = User.query.filter(
        User.name.ilike(f'%{query}%'),
        User.id != current_user.id
    ).limit(10).all()

    return jsonify([{"id": u.id, "name": u.name} for u in matches])
