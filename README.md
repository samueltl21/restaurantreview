# Restaurant Review Application

## Description

The Restaurant Review Application is a web-based platform designed to allow users to browse, review, and share their experiences at various restaurants. The application is built using Flask, a lightweight WSGI web application framework in Python. It features user authentication and authorization, enabling users to create accounts, log in, and manage their reviews. The design focuses on providing a user-friendly interface for seamless navigation and interaction.

## Group Members

| UWA ID   | Name                  | GitHub Username |
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
   - On macOS:
     ```bash
     source application-env/bin/activate
     ```
   - On Windows:
     ```bash
     application-env\Scripts\activate
     ```
5. **Install the required dependencies**
   ```bash
   pip install -r requirements.txt
   ```
6. **Load initial data**
   ```bash
   python3 seed.py
   ```
7. **Run the Flask application**
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
   python3 -m unittest tests.test_selenium_login
   python3 -m unittest tests.test_selenium_navigating_after_login
   python3 -m unittest tests.test_selenium_navigating_without_login
   python3 -m unittest tests.test_selenium_sharing_review
   python3 -m unittest tests.test_selenium_edit_review
   ```
   - The results will be displayed in the browser.

