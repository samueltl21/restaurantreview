# Restaurant Review Application

## Description

The Restaurant Review Application is a web-based platform designed to connect food enthusiasts and provide a space for sharing honest reviews and discovering new dining experiences. The platform aims to foster a community of food lovers who can explore and contribute to a growing database of restaurant reviews.

### Purpose

The primary goal of this platform is to offer users a reliable source of restaurant reviews, helping them make informed dining decisions. By allowing users to share their experiences, the application promotes transparency and trust within the community.

### Main Features

- **User Authentication and Authorization**: Secure login and account management for personalized experiences, ensuring that each user's data is protected and accessible only to them.
- **Review Submission and Management**: Users can submit reviews, rate restaurants, and edit their contributions, allowing for a dynamic and interactive community of food enthusiasts.
- **Data Visualization**: Personalized interactive charts and graphs to visualize each user's dining preferences and patterns.
- **Profile Management**: Users can manage their profiles, including viewing their review history and preferences, enhancing the personalization of their experience on the platform.
- **Review Sharing**: Users can share their reviews with other users, fostering community engagement and collaboration.

## Group Members

| Student ID   | Name                  | GitHub Username |
|----------|-----------------------|-----------------|
| 24452249 | Samuel Theodore       | samueltl21      |
| 24139199 | Mengting Zhang        | ZHMETI          |
| 23869695 | Shouvik Barua Pratik  | shouvikpratik   |
| 24144304 | Yunhua Feng           | Cherry5413      |

## Setup Guide

To launch the application, follow these steps:

1. **Clone the repository**
   ```bash
   git clone https://github.com/samueltl21/restaurantreview.git
   ```
2. **Navigate to the project directory**
   ```bash
   cd restaurantreview
   ```
3. **Create a virtual environment**
   ```bash
   python3 -m venv application-env
   ```
4. **Activate the virtual environment**
   - On macOS/Linux:
     ```bash
     source application-env/bin/activate
     ```
   - On Windows:
     ```bash
     .\application-env\Scripts\activate
     ```
5. **Install the required dependencies**
   ```bash
   pip install -r requirements.txt
   ```
6. **Set SECRET_KEY in environment**
   ```bash
   export SECRET_KEY=restaurant12345
   ```
7. **Load initial data**
   ```bash
   python3 seed.py
   ```
8. **Run the Flask application**
   ```bash
   flask run
   ```

## Running Tests

To ensure the application functions correctly, you can run the following tests:

### Unit Tests

1. **Authentication & Authorization Tests**
   ```bash
   python3 -m tests.test_auth
   ```
2. **Restaurant Review Tests**
   ```bash
   python3 -m tests.test_restaurant_review
   ```

### Selenium Tests

1. **Prepare the environment**
   - Follow all setup steps until running the Flask app.
   - Open a new terminal while the Flask app is running.

2. **Run Selenium Tests**
   ```bash
   python -m unittest tests.test_selenium_login
   ```
   ```bash
   python -m unittest tests.test_selenium_navigating_after_login
   ```
   ```bash
   python -m unittest tests.test_selenium_navigating_without_login
   ```
   ```bash
   python -m unittest tests.test_selenium_sharing_review
   ```
   ```bash
   python -m unittest tests.test_selenium_edit_review
   ```
   - The test results will be displayed in the browser.

