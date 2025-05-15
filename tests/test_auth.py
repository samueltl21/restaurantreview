import unittest
from app import db, create_app
from config import TestingConfig
from app.models import User
from werkzeug.security import generate_password_hash

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Create a test user for login
        hashed_pw = generate_password_hash('testpass')
        user = User(name="Alice", email="alice@example.com", password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_successful_login(self):
        response = self.client.post('/login', data={
            'email': 'alice@example.com',
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertIn(b'Login successful!', response.data)

    def test_failed_login_wrong_password(self):
        response = self.client.post('/login', data={
            'email': 'alice@example.com',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password!', response.data)

    def test_signup_new_user(self):
        response = self.client.post('/sign_up', data={
            'name': 'Bob',
            'email': 'bob@example.com',
            'password': 'securepass',
            'confirm_password': 'securepass'
        }, follow_redirects=True)
        self.assertIn(b'Sign up successful!', response.data)

        user = User.query.filter_by(email='bob@example.com').first()
        self.assertIsNotNone(user)
    
    def test_signup_existing_email(self):
        response = self.client.post('/sign_up', data={
            'name': 'Alice',
            'email': 'alice@example.com',
            'password': 'anypass',
            'confirm_password': 'anypass'
        }, follow_redirects=True)
        self.assertIn(b'Email already registered!', response.data)

    def test_logout(self):
        # Step 1: Log in
        self.client.post('/login', data={
            'email': 'alice@example.com',
            'password': 'testpass'
        }, follow_redirects=True)

        # Step 2: Logout
        response = self.client.get('/logout', follow_redirects=True)

        # Step 3: Check for confirmation message or redirect
        self.assertIn(b'You have been logged out', response.data)

    def test_access_after_logout(self):
        self.client.post('/login', data={
            'email': 'alice@example.com',
            'password': 'testpass'
        }, follow_redirects=True)

        self.client.get('/logout', follow_redirects=True)

        response = self.client.get('/profile', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

if __name__ == '__main__':
    unittest.main()
