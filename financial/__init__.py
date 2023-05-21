import logging as log
import os
from os import environ

import sqlalchemy
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

app = Flask(__name__)
ma = Marshmallow(app)


db_pass = os.environ.get("DB_PASS")
db_user = os.environ.get("DB_USER")
db = os.environ.get("DB")
db_host = os.environ.get("DB_HOST")

url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}"

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:3306/{db}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

try:
    db = SQLAlchemy(app)
except sqlalchemy.exc.ProgrammingError as e:
    print("error", e)

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

user_api_key = environ.get("RAW_API_KEY")
api_key = user_api_key if len(user_api_key) else "demo"

from financial.routes import *
