from flask_login import login_required
from app.blueprints import main
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

@main.route('/')
def index():
    return index_logic()

@main.route('/about_us')
def about_us():
    return about_us_logic()

@main.route('/profile')
@login_required
def profile():
    return profile_logic()

@main.route('/login', methods=['GET', 'POST'])
def login():
    return login_logic()

@main.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    return sign_up_logic()

@main.route('/logout')
@login_required
def logout():
    return logout_logic()

@main.route("/upload_reviews", methods=["GET", "POST"])
@login_required
def upload_reviews():
    return upload_reviews_logic()

@main.route('/check_restaurant', methods=['POST'])
def check_restaurant():
    return check_restaurant_logic()

@main.route('/search_restaurants', methods=['GET'])
def search_restaurants():
    return search_restaurants_logic()

@main.route('/restaurants/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    return restaurant_detail_logic(restaurant_id)

@main.route('/restaurants/<int:restaurant_id>/upload_image', methods=['POST'])
@login_required
def upload_restaurant_image(restaurant_id):
    return upload_restaurant_image_logic(restaurant_id)

@main.route("/share_reviews", methods=["POST"])
@login_required
def share_reviews():
    return share_reviews_logic()

@main.route('/shared/<token>', methods=["GET", "POST"])
@login_required
def view_shared_reviews(token):
    return view_shared_reviews_logic(token)

@main.route('/shared/conversation/<int:user_id>', methods=["GET", "POST"])
@login_required
def view_shared_conversation(user_id):
    return view_shared_conversation_logic(user_id)

@main.route('/shared_with')
@login_required
def shared_with():
    return shared_with_logic()

@main.route('/search_users', methods=['GET'])
@login_required
def search_users():
    return search_users_logic()

@main.route("/api/review/<int:review_id>", methods=["POST"])
@login_required
def api_update_review(review_id):
    return api_update_review_logic(review_id)
