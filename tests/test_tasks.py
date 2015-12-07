import unittest
from mock import patch
from base import BaseTestCase
from app.models import GrowSession, FlowerDevice, FlowerData, WaterDevice
from app.tasks import meassure
from datetime import datetime


class TestTaskHandler(BaseTestCase):
    def setUp(self):
        super(TestTaskHandler, self).setUp()

    def tearDown(self):
        super(TestTaskHandler, self).tearDown()
        self.db.session.query(GrowSession).delete()
        self.db.session.query(FlowerDevice).delete()
        self.db.session.query(WaterDevice).delete()
        self.db.session.commit()

    def make_data_session_flower(self):
        self.db.session.add(GrowSession(name="grow_session", start_date=datetime.now()))
        grow_session = self.db.session.query(GrowSession).first()
        self.db.session.add(FlowerDevice(name="flower",
                                         mac="A0:14:3D:08:B4:90",
                                         grow_session_id=grow_session.id))
        self.db.session.commit()

    def test_meassure_functioning(self):
        self.make_data_session_flower()
        data_points_before = len(self.db.session.query(FlowerData).all())
        meassure()
        data_points_after = len(self.db.session.query(FlowerData).all())
        self.assertEqual(data_points_before, data_points_after - 1, "Wrong number of insertions in meassure")

    def make_data_session_flower_multiple(self):
        self.db.session.add(GrowSession(name="grow_session", start_date=datetime.now()))
        grow_session = self.db.session.query(GrowSession).first()
        self.db.session.add(FlowerDevice(name="flower1",
                                         mac="A0:14:3D:08:B4:90",
                                         grow_session_id=grow_session.id))
        self.db.session.add(FlowerDevice(name="flower2",
                                         mac="A0:14:3D:08:B4:91",
                                         grow_session_id=grow_session.id))
        self.db.session.commit()

    def test_meassure_multiple_flowers(self):
        self.make_data_session_flower_multiple()
        data_points_before = len(self.db.session.query(FlowerData).all())
        meassure()
        data_points_after = len(self.db.session.query(FlowerData).all())
        self.assertEqual(data_points_before, data_points_after - 2, "Wrong number of insertions in meassure")

    def make_data_watering(self):
        self.db.session.add(GrowSession(name="grow_session", start_date=datetime.now()))
        grow_session = self.db.session.query(GrowSession).first()
        self.db.session.add(FlowerDevice(name="flower",
                                         mac="A0:14:3D:08:B4:90",
                                         grow_session_id=grow_session.id))
        self.db.session.add(WaterDevice(name="water",
                                        key="10011",
                                        device=1,
                                        grow_session_id=grow_session.id,
                                        water_threshhold=100.0))
        self.db.session.commit()

    @patch('app.tasks.start_water')
    def test_measure_with_watering(self, start_water_mock):
        self.make_data_watering()
        meassure()
        water_id = self.db.session.query(WaterDevice).first().id
        start_water_mock.assert_called_once_with(water_id)

if __name__ == '__main__':
    unittest.main()
