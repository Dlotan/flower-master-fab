import unittest
from datetime import datetime
from base import BaseTestCase
from app.hub import send_email, new_data_point
from app.models import GrowSession, FlowerDevice, FlowerData


class TestHub(BaseTestCase):
    def tearDown(self):
        super(TestHub, self).tearDown()
        self.db.session.query(GrowSession).delete()
        self.db.session.query(FlowerDevice).delete()
        self.db.session.query(FlowerData).delete()
        self.db.session.commit()

    def test_send_email(self):
        pass
        """success = send_email("testreciever", "testsubject", "testbody")
        self.assertEqual(success, True, "Failed to send email")"""

    def make_data_flower_data(self):
        self.db.session.add(GrowSession(name="grow_session", start_date=datetime.now()))
        grow_session = self.db.session.query(GrowSession).first()
        self.db.session.add(FlowerDevice(name="flower",
                                         mac="A0:14:3D:08:B4:90",
                                         grow_session_id=grow_session.id))
        flower_device = self.db.session.query(FlowerDevice).first()
        data = dict(Temperature=10.23, Light=100, Water=50.0, Battery=90, Ecb=0.5,
                    EcPorus=0.6, DLI=0.7, Ea=0.8, )
        self.db.session.add(FlowerData.new_flower_data(data, flower_device.id, flower_device.grow_session.id))
        self.db.session.commit()

    def test_new_data(self):
        pass
        """self.make_data_flower_data()
        flower_data = self.db.session.query(FlowerData).first()
        data = flower_data.get_data_dict()
        success = new_data_point(data, "flower", "session")
        self.assertEqual(success, True, "Failed to send new data to server")"""


if __name__ == '__main__':
    unittest.main()
