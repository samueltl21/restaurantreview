from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

application = Flask(__name__)
application.config.from_object(Config)

db = SQLAlchemy(application)

import app.routes