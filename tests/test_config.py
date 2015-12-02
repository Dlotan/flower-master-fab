import unittest
from flask import current_app
from flask.ext.testing import TestCase
from app import create_application


class TestProductionConfig(TestCase):
    def create_app(self):
        return create_application('production')

    def test_app_is_testing(self):
        assert current_app.config['HARDWARE'] == True


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        return create_application('development')

    def test_app_is_developing(self):
        assert current_app.config['HARDWARE'] == False


class TestTestConfig(TestCase):
    def create_app(self):
        return create_application('testing')

    def test_app_is_testing(self):
        assert current_app.config['HARDWARE'] == False


if __name__ == '__main__':
    unittest.main()
