# restaurantreview
A group project for CITS5505

Team Setup Guide:

1. Clone the repo
In terminal:
git clone https://github.com/samueltl21/restaurantreview.git

2. Change to the directory:
cd restaurantreview

3. Create a virtual environment:
python3 -m venv application-env

4. Activate
macOS:
source application-env/bin/activate
Windows:
application-env\Scripts\activate

5. Install all required dependancies from requirements.txt:
pip install -r requirements.txt 

6. Load seed.py data
python3 seed.py

7. Run the Flask app:
flask run

=====
Testing unittest:
Do all steps until step 6,
Then:
a. Run the unittest for authentication & authorization (6 tests)
python3 -m tests.test_auth
b. Run the unittest for restaurant review test (8 tests)
python3 -m tests.test_restaurant_review

=====
Testing with selenium:
Do all steps until step 7,
Then open another terminal/command line while another terminal run the "flask run"

After that, run selenium test:
python3 -m unittest tests.test_selenium_login
python3 -m unittest tests.test_selenium_navigating_after_login
python3 -m unittest tests.test_selenium_navigating_without_login
python3 -m unittest tests.test_selenium_sharing_review
python3 -m unittest tests.test_selenium_edit_review
** the browser will play the test scenario