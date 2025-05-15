from app import application
from flask_login import login_required
from app.controllers import (
    index_logic,
    about_us_logic,
    profile_logic,
    login_logic,
    sign_up_logic,
    logout_logic,
    upload_reviews_logic,
    check_restaurant_logic,
    search_restaurants_logic,
    restaurant_detail_logic,
    upload_restaurant_image_logic,
    share_reviews_logic,
    view_shared_reviews_logic,
    view_shared_conversation_logic,
    shared_with_logic,
    search_users_logic,
    api_update_review_logic
)

@application.route('/')
def index():
    return index_logic()

@application.route('/about_us')
def about_us():
    return about_us_logic()

@application.route('/profile')
@login_required
def profile():
    return profile_logic()

@application.route('/login', methods=['GET', 'POST'])
def login():
    return login_logic()

@application.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    return sign_up_logic()

@application.route('/logout')
@login_required
def logout():
    return logout_logic()

@application.route("/upload_reviews", methods=["GET", "POST"])
@login_required
def upload_reviews():
    return upload_reviews_logic()

@application.route('/check_restaurant', methods=['POST'])
def check_restaurant():
    return check_restaurant_logic()

@application.route('/search_restaurants', methods=['GET'])
def search_restaurants():
    return search_restaurants_logic()

@application.route('/restaurants/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    return restaurant_detail_logic(restaurant_id)

@application.route('/restaurants/<int:restaurant_id>/upload_image', methods=['POST'])
@login_required
def upload_restaurant_image(restaurant_id):
    return upload_restaurant_image_logic(restaurant_id)

@application.route("/share_reviews", methods=["POST"])
@login_required
def share_reviews():
    return share_reviews_logic()

@application.route('/shared/<token>', methods=["GET", "POST"])
@login_required
def view_shared_reviews(token):
    return view_shared_reviews_logic(token)

@application.route('/shared/conversation/<int:user_id>', methods=["GET", "POST"])
@login_required
def view_shared_conversation(user_id):
    return view_shared_conversation_logic(user_id)

@application.route('/shared_with')
@login_required
def shared_with():
    return shared_with_logic()

@application.route('/search_users', methods=['GET'])
@login_required
def search_users():
    return search_users_logic()

@application.route("/api/review/<int:review_id>", methods=["POST"])
@login_required
def api_update_review(review_id):
    return api_update_review_logic(review_id)
