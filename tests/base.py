import unittest
from app.config import config

from app import app, db


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        app.config.from_object(config['testing'])
        self.app = app
        self.c = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
