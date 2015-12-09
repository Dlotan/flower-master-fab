import unittest
from app.config import config
from app import app


class TestProductionConfig(unittest.TestCase):
    def setUp(self):
        app.config.from_object(config['production'])
        self.app = app

    def test_app_is_production(self):
        self.assertTrue(self.app.config['HARDWARE'])
        self.assertTrue(self.app.config['WEBCAM'])


class TestDevelopmentConfig(unittest.TestCase):
    def setUp(self):
        app.config.from_object(config['development'])
        self.app = app

    def test_app_is_development(self):
        self.assertFalse(self.app.config['HARDWARE'])
        self.assertFalse(self.app.config['WEBCAM'])


class TestTestConfig(unittest.TestCase):
    def setUp(self):
        app.config.from_object(config['testing'])
        self.app = app

    def test_app_is_testing(self):
        self.assertFalse(self.app.config['HARDWARE'])
        self.assertFalse(self.app.config['WEBCAM'])


if __name__ == '__main__':
    unittest.main()
