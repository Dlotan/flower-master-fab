import unittest
from mock import patch
from base import BaseTestCase
from app.models import GrowSession, FlowerDevice, FlowerData, WaterDevice, Subscriber
from app import tasks
from datetime import datetime


class TestTasks(BaseTestCase):
    def setUp(self):
        super(TestTasks, self).setUp()

    def tearDown(self):
        super(TestTasks, self).tearDown()
        self.db.session.query(GrowSession).delete()
        self.db.session.query(FlowerDevice).delete()
        self.db.session.query(WaterDevice).delete()
        self.db.session.query(Subscriber).delete()
        self.db.session.commit()
        if tasks.scheduler:
            tasks.scheduler = None

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
        tasks.meassure()
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
        tasks.meassure()
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
        tasks.meassure()
        water_id = self.db.session.query(WaterDevice).first().id
        start_water_mock.assert_called_once_with(water_id)

    def make_subscriber_data(self):
        self.db.session.add(GrowSession(name="grow_session", start_date=datetime.now()))
        grow_session = self.db.session.query(GrowSession).first()
        self.db.session.add(FlowerDevice(name="flower",
                                         mac="A0:14:3D:08:B4:90",
                                         grow_session_id=grow_session.id))
        flower_device = self.db.session.query(FlowerDevice).first()
        data = dict(Temperature=10.23, Light=100, Water=50.0, Battery=90, Ecb=0.5,
                    EcPorus=0.6, DLI=0.7, Ea=0.8, )
        self.db.session.add(FlowerData.new_flower_data(data, flower_device.id, flower_device.grow_session.id))
        self.db.session.add(Subscriber(name="test", receiver_email="test@test.com", grow_session_id=grow_session.id))
        self.db.session.commit()

    @patch('app.hub.send_email')
    def test_update_subscribers(self, send_email_mock):
        self.make_subscriber_data()
        send_email_mock.return_value = True
        tasks.update_subscribers()
        self.assertEqual(send_email_mock.called, True, "Didn't try to send email")


if __name__ == '__main__':
    unittest.main()
