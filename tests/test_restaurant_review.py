import unittest
import io
import os
from app import db, create_app
from config import TestingConfig
from app.models import User, Restaurant, Review
from werkzeug.security import generate_password_hash

class ReviewTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Create user
        hashed_pw = generate_password_hash('testpass')
        self.user = User(name="Alice", email="alice@example.com", password_hash=hashed_pw)
        db.session.add(self.user)
        db.session.commit()

        # Create existing restaurant
        self.restaurant = Restaurant(name="Spicy Noodle House", location="Northbridge", cuisine="Thai", added_by=self.user.id)
        db.session.add(self.restaurant)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        return self.client.post('/login', data={
            'email': 'alice@example.com',
            'password': 'testpass'
        }, follow_redirects=True)

    def test_review_existing_restaurant(self):
        self.login()

        response = self.client.post('/upload_reviews', data={
            'restaurant': 'Spicy Noodle House',
            'location': 'Northbridge',  # only for testing
            'cuisine': 'Thai',          # because backend will read the form without checking if it exists
            'date': '2025-05-15',
            'rating': '4',
            'spend': '29.90',
            'comment': 'Delicious noodles and friendly service!',
            'submit': 'Submit Rating' 
        }, follow_redirects=True)

        self.assertIn(b'Thanks for your review!', response.data)

        review = Review.query.filter_by(user_id=self.user.id, restaurant_id=self.restaurant.id).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.comment, 'Delicious noodles and friendly service!')

    def test_review_new_restaurant(self):
        self.login()

        response = self.client.post('/upload_reviews', data={
            'restaurant': 'Ocean Breeze',
            'location': 'Fremantle',
            'cuisine': 'Thai',
            'date': '2025-05-16',
            'rating': '5',
            'spend': '45.00',
            'comment': 'Fresh fish and a beautiful view!',
            'submit': 'Submit Rating'
        }, follow_redirects=True)

        self.assertIn(b'Thanks for your review!', response.data)

        restaurant = Restaurant.query.filter_by(name='Ocean Breeze').first()
        self.assertIsNotNone(restaurant)
        review = Review.query.filter_by(user_id=self.user.id, restaurant_id=restaurant.id).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.comment, 'Fresh fish and a beautiful view!')

    def test_missing_rating(self):
        self.login()
        response = self.client.post('/upload_reviews', data={
            'restaurant': 'Spicy Noodle House',
            'date': '2025-05-15',
            'spend': '29.90',
            'comment': 'Tasty but forgot to rate!',
            'submit': 'Submit Rating'
        }, follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

    def test_missing_restaurant_name(self):
        self.login()
        response = self.client.post('/upload_reviews', data={
            'restaurant': '',
            'date': '2025-05-15',
            'rating': '4',
            'spend': '29.90',
            'comment': 'Missing restaurant name',
            'submit': 'Submit Rating'
        }, follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

    def test_all_fields_missing(self):
        self.login()
        response = self.client.post('/upload_reviews', data={
            'restaurant': '',
            'date': '',
            'rating': '',
            'spend': '',
            'comment': '',
            'submit': 'Submit Rating'
        }, follow_redirects=True)
        self.assertIn(b'This field is required', response.data)

    def test_negative_spending_amount(self):
        self.login()
        response = self.client.post('/upload_reviews', data={
            'restaurant': 'Spicy Noodle House',
            'location': 'Northbridge',
            'cuisine': 'Thai',
            'date': '2025-05-15',
            'rating': '4',
            'spend': '-5.00',
            'comment': 'Too cheap to be true',
            'submit': 'Submit Rating'
        }, follow_redirects=True)

        self.assertIn(b'Number must be at least 0', response.data)

    def test_upload_valid_image_review(self):
        self.login()
        image_path = os.path.join('app', 'static', 'images', 'home-food.jpg')
        with open(image_path, 'rb') as img:
            data = {
                'restaurant': 'Spicy Noodle House',
                'location': 'Northbridge',
                'cuisine': 'Thai',
                'date': '2025-05-15',
                'rating': '4',
                'spend': '29.90',
                'comment': 'Uploading a valid image!',
                'submit': 'Submit Rating',
                'review_image': (img, 'home-food.jpg')
            }
            response = self.client.post('/upload_reviews', data=data, content_type='multipart/form-data', follow_redirects=True)

        self.assertIn(b'Thanks for your review!', response.data)
        review = Review.query.filter_by(user_id=self.user.id, restaurant_id=self.restaurant.id).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.comment, 'Uploading a valid image!')
        self.assertTrue(review.image.endswith('home-food.jpg'))

    def test_upload_invalid_file_review(self):
        self.login()

        data = {
            'restaurant': 'Spicy Noodle House',
            'location': 'Northbridge',
            'cuisine': 'Thai',
            'date': '2025-05-15',
            'rating': '4',
            'spend': '29.90',
            'comment': 'Trying to upload invalid file!',
            'submit': 'Submit Rating',
            'review_image': (io.BytesIO(b"not an image"), 'document.pdf')
        }

        response = self.client.post('/upload_reviews', data=data, content_type='multipart/form-data', follow_redirects=True)

        self.assertIn(b'Images only!', response.data)


if __name__ == '__main__':
    unittest.main()

