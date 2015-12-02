import logging

from flask import Flask
from flask.ext.appbuilder import SQLA, AppBuilder

from app.config import config

"""
 Logging configuration
"""

db = SQLA()
appbuilder = AppBuilder()


def create_application(config_name):
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    logging.getLogger().setLevel(logging.ERROR)

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    ctx = app.app_context()
    ctx.push()
    appbuilder.init_app(app, db.session)

    return app

from app import views
