import logging

from flask import Flask
from flask.ext.appbuilder import SQLA, AppBuilder
import os

from app.config import config


logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.ERROR)

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_CONFIG') or 'default'])
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

from app import views
