from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

application = Flask(__name__)
application.config.from_object('app.config.Config')

db = SQLAlchemy(application)

import app.routes