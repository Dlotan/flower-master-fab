from app import db, appbuilder
from app.models import LightDevice, GrowSession, WaterDevice, FlowerDevice
from datetime import datetime, timedelta

db.create_all()
role_admin = appbuilder.sm.find_role(appbuilder.sm.auth_role_admin)
appbuilder.sm.add_user('Dlotan', 'Admin', 'User', 'admin@dlotan.org', role_admin, 'dlotan')


db.session.add(GrowSession(name="grow_session"))
grow_session = db.session.query(GrowSession).first()
db.session.add(LightDevice(name="light", key="10011", device=1, grow_session_id=grow_session.id))
light_device = db.session.query(LightDevice).first()
db.session.add(WaterDevice(name="water", key="10011", device=2, grow_session_id=grow_session.id))
water_device = db.session.query(WaterDevice).first()
db.session.add(FlowerDevice(name="flower", mac="A0:14:3D:08:B4:90", grow_session_id=grow_session.id))
flower_device = db.session.query(FlowerDevice).first()
db.session.commit()

for i in range(50):
    from app.models import FlowerData
    datapoint = FlowerData(
        timestamp=datetime.now()-timedelta(minutes=i),
        temperature=10.23 + i*0.1,
        light=100,
        water=40.5 - i*0.5,
        battery=90 - i,
        ecb=0.5,
        ec_porus=0.6,
        dli=0.7,
        ea=0.8,
        flower_device_id=flower_device.id,
        grow_session_id=grow_session.id,
    )
    db.session.add(datapoint)
db.session.commit()
