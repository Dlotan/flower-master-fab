import unittest
from base import BaseTestCase


class TestMainHandler(BaseTestCase):
    def test_basic_routes_functioning(self):
        with self.c as c:
            rv = c.get('/')
            self.assertEqual(rv.status_code, 200, 'Unable to access index')
            rv = c.get('/login/')
            self.assertEqual(rv.status_code, 200, 'Unable to access login')


if __name__ == '__main__':
    unittest.main()
