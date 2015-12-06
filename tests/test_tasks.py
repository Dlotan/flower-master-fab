import unittest
from base import BaseTestCase
from app.models import GrowSession, FlowerDevice, FlowerData
from app.tasks import meassure
from datetime import datetime


class TestTaskHandler(BaseTestCase):
    def setUp(self):
        super(TestTaskHandler, self).setUp()
        self.db.session.add(GrowSession(name="grow_session", start_date=datetime.now()))
        grow_session = self.db.session.query(GrowSession).first()
        self.db.session.add(FlowerDevice(name="flower",
                                         mac="A0:14:3D:08:B4:90",
                                         grow_session_id=grow_session.id))
        self.db.session.commit()

    def tearDown(self):
        super(TestTaskHandler, self).tearDown()
        self.db.session.query(GrowSession).delete()
        self.db.session.query(FlowerDevice).delete()
        self.db.session.commit()

    def test_meassure_functioning(self):
        data_points_before = len(self.db.session.query(FlowerData).all())
        meassure()
        data_points_after = len(self.db.session.query(FlowerData).all())
        self.assertEqual(data_points_before, data_points_after - 1, "Wrong number of insertions in meassure")
if __name__ == '__main__':
    unittest.main()
