import unittest
from freezegun import freeze_time
from datetime import datetime
from base import BaseTestCase
from app.models import GrowSession, FlowerDevice, FlowerData, Subscriber, LightDevice


class TestModel(BaseTestCase):
    def tearDown(self):
        super(TestModel, self).tearDown()
        self.db.session.query(GrowSession).delete()
        self.db.session.query(FlowerDevice).delete()
        self.db.session.query(FlowerData).delete()
        self.db.session.query(Subscriber).delete()
        self.db.session.query(LightDevice).delete()
        self.db.session.commit()

    def make_data_grow_session(self):
        self.db.session.add(GrowSession(name="grow_session", start_date=datetime.now()))
        self.db.session.add(GrowSession(name="grow_session2"))
        self.db.session.commit()

    def test_grow_session(self):
        self.make_data_grow_session()
        self.assertEqual(len(GrowSession.get_active()), 1, "Number of active grow sessions is wrong")
        grow_session = GrowSession.get_active()[0]
        self.assertTrue(grow_session.is_active())
        grow_session2 = GrowSession.get_inactive()[0]
        self.assertFalse(grow_session2.is_active())

    def make_data_grow_seesion_day_night(self):
        self.db.session.add(GrowSession(name="grow_session"))

    def test_grow_session_day_night(self):
        self.make_data_grow_seesion_day_night()
        grow_session = self.db.session.query(GrowSession).first()
        grow_session.day_start_hour = 8
        grow_session.night_start_hour = 23
        with freeze_time("1-1-2016 12:00:00"):
            self.assertTrue(grow_session.is_day())
        with freeze_time("1-1-2016 7:00:00"):
            self.assertTrue(grow_session.is_night())
        with freeze_time("1-1-2016 8:00:00"):
            self.assertTrue(grow_session.is_day())
        with freeze_time("1-1-2016 23:00:00"):
            self.assertTrue(grow_session.is_night())
        grow_session.day_start_hour = 8
        grow_session.night_start_hour = 7
        with freeze_time("1-1-2016 12:00:00"):
            self.assertTrue(grow_session.is_day())
        with freeze_time("1-1-2016 7:30:00"):
            self.assertTrue(grow_session.is_night())
        with freeze_time("1-1-2016 8:00:00"):
            self.assertTrue(grow_session.is_day())
        with freeze_time("1-1-2016 7:00:00"):
            self.assertTrue(grow_session.is_night())

    def make_data_subscriber(self):
        self.db.session.add(GrowSession(name="grow_session", start_date=datetime.now()))
        grow_session = GrowSession.get_active()[0]
        self.db.session.add(Subscriber(name="test_subscriber", grow_session_id=grow_session.id))
        self.db.session.add(GrowSession(name="grow_session2"))
        grow_session2 = GrowSession.get_inactive()[0]
        self.db.session.add(Subscriber(name="test_subscriber2", grow_session_id=grow_session2.id))
        self.db.session.commit()

    def test_subscriber(self):
        self.make_data_subscriber()
        grow_sessions = self.db.session.query(GrowSession).all()
        for grow_session in grow_sessions:
            self.assertEqual(len(grow_session.subscribers), 1)
        self.assertEqual(len(Subscriber.get_active()), 1)

if __name__ == '__main__':
    unittest.main()
