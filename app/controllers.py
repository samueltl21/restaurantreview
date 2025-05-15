from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func
from app import db
from app.models import User, Restaurant, Review, SharedReview, SharedComment, SharedReviewEntry
from app.forms import LoginForm, SignUpForm, ReviewForm
from datetime import datetime
import os
import uuid
import json
from collections import defaultdict

def check_restaurant_logic():
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

def search_restaurants_logic():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    matches = Restaurant.query.filter(Restaurant.name.ilike(f"%{query}%")).limit(10).all()
    return jsonify([r.name for r in matches])

def search_restaurants_logic():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    matches = Restaurant.query.filter(Restaurant.name.ilike(f"%{query}%")).limit(10).all()
    return jsonify([r.name for r in matches])

def restaurant_detail_logic(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    reviews = Review.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('restaurant_detail.html', restaurant=restaurant, reviews=reviews)

def upload_restaurant_image_logic(restaurant_id):
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

def index_logic():
    restaurants = (
        db.session.query(Restaurant, func.avg(Review.rating).label("avg_rating"))
        .outerjoin(Review, Review.restaurant_id == Restaurant.id)
        .group_by(Restaurant.id)
        .all()
    )
    sorted_by_rating = sorted(restaurants, key=lambda x: x[1] or 0, reverse=True)
    top_restaurants = sorted_by_rating[:3]
    grouped = defaultdict(list)
    for restaurant, avg_rating in restaurants:
        grouped[restaurant.cuisine].append((restaurant, round(avg_rating or 0, 1)))
    return render_template("restaurants.html", grouped_restaurants=grouped, top_restaurants=top_restaurants)

def about_us_logic():
    return render_template('about_us.html')

def login_logic():
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

def sign_up_logic():
    form = SignUpForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
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

def logout_logic():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

def upload_reviews_logic():
    form = ReviewForm()
    if form.validate_on_submit():
        restaurant_name = form.restaurant.data.strip()
        location = form.location.data.strip()
        cuisine = form.cuisine.data.strip()
        rating = int(form.rating.data)
        date = form.date.data.strftime('%Y-%m-%d')
        spend = float(form.spend.data)
        restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
        if not restaurant:
            restaurant = Restaurant(name=restaurant_name, location=location, cuisine=cuisine, added_by=current_user.id)
            db.session.add(restaurant)
            db.session.flush()
        existing_review = Review.query.filter_by(user_id=current_user.id, restaurant_id=restaurant.id, date=date).first()
        if existing_review:
            flash("You've already submitted a review for this restaurant on that date", "warning")
            return redirect(url_for("upload_reviews"))
        review = Review(rating=rating, date=date, spend=spend, user_id=current_user.id, restaurant_id=restaurant.id)
        file = form.review_image.data
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join("app/static/images", filename)
            file.save(path)
            review.image = filename
        review.comment = form.comment.data
        db.session.add(review)
        db.session.commit()
        flash("Thanks for your review!", "success")
        return redirect(url_for("index"))
    return render_template("upload_reviews.html", form=form)

def profile_logic():
    from sqlalchemy import desc

    # 🧠 Get all reviews for statistics
    all_reviews = Review.query.filter_by(user_id=current_user.id).all()

    # 🧠 Initialize containers
    cuisine_counts = {}
    cuisine_spend = {}
    cuisine_spend_count = {}
    total_rating = 0
    total_spend = 0
    num_reviews = len(all_reviews)

    # 🧠 Calculate statistics
    for review in all_reviews:
        if review.restaurant:
            cuisine = review.restaurant.cuisine
            cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
            cuisine_spend[cuisine] = cuisine_spend.get(cuisine, 0) + review.spend
            cuisine_spend_count[cuisine] = cuisine_spend_count.get(cuisine, 0) + 1
            total_rating += review.rating
            total_spend += review.spend

    avg_spend_by_cuisine = {
        cuisine: round(cuisine_spend[cuisine] / cuisine_spend_count[cuisine], 2)
        for cuisine in cuisine_spend
    }

    cuisine_labels = list(cuisine_counts.keys())
    cuisine_values = list(cuisine_counts.values())
    avg_spend_labels = list(avg_spend_by_cuisine.keys())
    avg_spend_values = list(avg_spend_by_cuisine.values())
    avg_rating = round(total_rating / num_reviews, 1) if num_reviews > 0 else 0
    avg_spend = round(total_spend / num_reviews, 2) if num_reviews > 0 else 0

    # 📄 Paginate reviews for table (3 per page, newest first)
    page = request.args.get('page', 1, type=int)
    per_page = 3
    pagination = Review.query.filter_by(user_id=current_user.id).order_by(desc(Review.date)).paginate(page=page, per_page=per_page)
    user_reviews = pagination.items

    # 👤 Get list of other users for sharing functionality
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
        all_users=all_users,
        reviews=user_reviews,         # 👈 paginated 3 reviews
        pagination=pagination         # 👈 pagination object
    )

def share_reviews_logic():
    data = request.get_json()
    review_ids = data.get("review_ids")
    recipient_id = data.get("recipient_id")

    if not review_ids or not recipient_id:
        return jsonify({"success": False, "message": "Missing data"}), 400

    recipient = User.query.get(recipient_id)
    if not recipient:
        return jsonify({"success": False, "message": "Recipient not found"}), 404

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
        combined_ids = existing_ids + new_ids
        existing_thread.review_ids = json.dumps(combined_ids)
        for review_id in new_ids:
            already_exists = SharedReviewEntry.query.filter_by(
                shared_review_id=existing_thread.id, review_id=review_id).first()
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
        db.session.flush()
        for review_id in review_ids:
            entry = SharedReviewEntry(
                shared_review_id=shared.id,
                review_id=review_id,
                shared_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            db.session.add(entry)
        db.session.commit()
        return jsonify({"success": True, "url": url_for("view_shared_conversation", user_id=recipient_id)})

def view_shared_reviews_logic(token):
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

    review_ids = list(set(json.loads(shared.review_ids)))
    reviews = Review.query.filter(Review.id.in_(review_ids)).all()
    sender = User.query.get(shared.sender_id)
    recipient = User.query.get(shared.recipient_id)
    comments = SharedComment.query.filter_by(shared_review_id=shared.id).order_by(SharedComment.timestamp).all()
    return render_template("shared_reviews.html", reviews=reviews, sender=sender, recipient=recipient, comments=comments)

def view_shared_conversation_logic(user_id):
    other_user = User.query.get_or_404(user_id)
    if other_user.id == current_user.id:
        flash("Cannot view a conversation with yourself.", "warning")
        return redirect(url_for("profile"))

    shared_threads = SharedReview.query.filter(
        ((SharedReview.sender_id == current_user.id) & (SharedReview.recipient_id == other_user.id)) |
        ((SharedReview.sender_id == other_user.id) & (SharedReview.recipient_id == current_user.id))
    ).all()

    if not shared_threads:
        flash("No shared history found with this user.", "info")
        return redirect(url_for("shared_with"))

    shared_thread_ids = [thread.id for thread in shared_threads]
    entry_data = (
        db.session.query(SharedReviewEntry, Review, SharedReview, User)
        .join(Review, SharedReviewEntry.review_id == Review.id)
        .join(SharedReview, SharedReviewEntry.shared_review_id == SharedReview.id)
        .join(User, SharedReview.sender_id == User.id)
        .filter(SharedReviewEntry.shared_review_id.in_(shared_thread_ids))
        .all()
    )
    timeline = []
    seen_review_ids = set()
    for entry, review, thread, sender in entry_data:
        if review.id not in seen_review_ids:
            timeline.append({"type": "review", "timestamp": entry.shared_at, "data": review, "sender": sender})
            seen_review_ids.add(review.id)
    comments = SharedComment.query.filter(
        SharedComment.shared_review_id.in_(shared_thread_ids)
    ).order_by(SharedComment.timestamp).all()
    for comment in comments:
        timeline.append({"type": "comment", "timestamp": comment.timestamp, "data": comment, "sender": comment.user})
    timeline.sort(key=lambda x: x["timestamp"])

    if request.method == "POST":
        content = request.form.get("comment", "").strip()
        if content:
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

def shared_with_logic():
    threads = SharedReview.query.filter(
        (SharedReview.sender_id == current_user.id) | (SharedReview.recipient_id == current_user.id)
    ).all()
    user_ids = set()
    for thread in threads:
        user_ids.add(thread.sender_id if thread.sender_id != current_user.id else thread.recipient_id)
    users = User.query.filter(User.id.in_(user_ids)).all()
    return render_template("shared_with.html", shared_users=users, has_shared_users=len(users) > 0)

def search_users_logic():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])
    matches = User.query.filter(
        User.name.ilike(f'%{query}%'), User.id != current_user.id
    ).limit(10).all()
    return jsonify([{"id": u.id, "name": u.name} for u in matches])

def api_update_review_logic(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    review.rating = int(request.form.get("rating", review.rating))
    review.spend = float(request.form.get("spend", review.spend))
    review.date = request.form.get("date", review.date)
    review.comment = request.form.get("comment", review.comment)

    if "review_image" in request.files:
        file = request.files["review_image"]
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            path = os.path.join("app/static/images", filename)
            file.save(path)
            review.image = filename

    if request.form.get("delete_image") == "on":
        review.image = None

    db.session.commit()
    return jsonify({"success": True})
