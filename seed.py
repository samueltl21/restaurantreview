from app import application, db
from app.models import User, Restaurant, Review, SharedReview, SharedReviewEntry, SharedComment
from werkzeug.security import generate_password_hash
from datetime import datetime
import json
import uuid

with application.app_context():
    # Reset DB
    db.drop_all()
    db.create_all()

    # Users
    user1 = User(name="testing", email="testing@testing.com", password_hash=generate_password_hash("testing"))
    user2 = User(name="abc", email="abc@testing.com", password_hash=generate_password_hash("abc"))
    user3 = User(name="123", email="123@testing.com", password_hash=generate_password_hash("123"))
    db.session.add_all([user1, user2, user3])
    db.session.commit()

    # Restaurants
    rest1 = Restaurant(name="Golden Spoon", location="North Perth", cuisine="Indian", added_by=user1.id, image="Golden_Spoon.jpg")
    rest2 = Restaurant(name="Midnight Bites", location="Subiaco", cuisine="Arabian", added_by=user2.id, image="Midnight_Bites.jpg")
    rest3 = Restaurant(name="The Spice House", location="Mount Lawley", cuisine="Thai", added_by=user3.id, image="The_Spice_House.jpg")
    rest4 = Restaurant(name="Ocean Delight", location="Fremantle", cuisine="Seafood", added_by=user1.id, image="Ocean_Delight.png")
    rest5 = Restaurant(name="FlavorTown", location="Cannington", cuisine="Fusion", added_by=user2.id, image="Flavor_Town.png")
    db.session.add_all([rest1, rest2, rest3, rest4, rest5])
    db.session.commit()

    # Reviews
    review1 = Review(date="2025-05-01", rating=4, spend=25.00, user_id=user1.id, restaurant_id=rest1.id, comment="Amazing butter chicken!")
    review2 = Review(date="2025-05-02", rating=5, spend=30.00, user_id=user2.id, restaurant_id=rest2.id, comment="Great Arabian grill set.")
    review3 = Review(date="2025-05-03", rating=3, spend=22.50, user_id=user3.id, restaurant_id=rest3.id, comment="Nice Tom Yum soup.")
    review4 = Review(date="2025-05-04", rating=4, spend=28.00, user_id=user1.id, restaurant_id=rest2.id, comment="Loved the lamb skewers.")
    review5 = Review(date="2025-05-05", rating=5, spend=35.00, user_id=user2.id, restaurant_id=rest4.id, comment="Seafood platter was super fresh!")
    review6 = Review(date="2025-05-06", rating=4, spend=27.00, user_id=user3.id, restaurant_id=rest5.id, comment="Interesting fusion dishes.")
    db.session.add_all([review1, review2, review3, review4, review5, review6])
    db.session.commit()

    # Shared Review (Alice → Bob)
    shared_token = str(uuid.uuid4())
    shared = SharedReview(
        sender_id=user1.id,
        recipient_id=user2.id,
        token=shared_token,
        review_ids=json.dumps([review1.id, review4.id]),
        shared_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(shared)
    db.session.flush()

    # SharedReviewEntries
    entry1 = SharedReviewEntry(shared_review_id=shared.id, review_id=review1.id, shared_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    entry2 = SharedReviewEntry(shared_review_id=shared.id, review_id=review4.id, shared_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.session.add_all([entry1, entry2])

    # Comment on shared review
    comment = SharedComment(
        shared_review_id=shared.id,
        user_id=user2.id,
        content="Can't wait to try this restaurant!",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(comment)

    db.session.commit()

    print("Seed data loaded successfully.")
