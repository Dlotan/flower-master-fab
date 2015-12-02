from flask.ext.testing import TestCase
from app import create_application, db


class BaseTestCase(TestCase):

    def create_app(self):
        return create_application('testing')

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
