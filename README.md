# Restaurantreview

## Description

A group project for CITS5505

## Setup Guide:

1. Clone the repo
In terminal:
    ```bash
    git clone https://github.com/samueltl21/restaurantreview.git
    ```
2. Change to the directory:
    ```bash
    cd restaurantreview
    ```
3. Create a virtual environment:
    ```bash
    python3 -m venv application-env
    ```
4. Activate
   - macOS:
   ```bash
   source application-env/bin/activate
    ```
    - Windows:
    ```bash
    application-env\Scripts\activate
    ```
5. Install all required dependancies from requirements.txt:
    ```bash
    pip install -r requirements.txt 
    ```
6. Load seed.py data
    ```bash
    python3 seed.py
    ```
7. Run the Flask app:
    ```bash
    flask run
    ```

## Testing unittest

Do all steps **until step 6**,

Then:

- Run the unittest for authentication & authorization (6 tests)
    ```bash
    python3 -m tests.test_auth
    ```
- Run the unittest for restaurant review test (8 tests)
    ```bash
    python3 -m tests.test_restaurant_review
    ```

## Testing with selenium

Do all steps **until step 7**,

- Then open another terminal/command line while another terminal run the `flask run`

- After that, run selenium test:
    ```bash
    python3 -m unittest tests.test_selenium_login
    python3 -m unittest tests.test_selenium_navigating_after_login
    python3 -m unittest tests.test_selenium_navigating_without_login
    python3 -m unittest tests.test_selenium_sharing_review
    python3 -m unittest tests.test_selenium_edit_review
    ```
- The result would be rendered in the browser.