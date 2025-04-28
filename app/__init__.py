from flask import Flask
from flask_sqlalchemy import SQLAlchemy

application = Flask(__name__)

application.secret_key = 'restaurantreview123'

application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

import app.routes