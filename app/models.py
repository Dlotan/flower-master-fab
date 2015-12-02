from flask.ext.appbuilder import Model
from flask.ext.appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, REAL, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import appbuilder, db

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""


def new_event(text):
    print(text)
    db.session.add(EventLog(text=text))
    db.session.commit()


class EventLog(Model):
    __tablename__ = 'event_log'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True, default=func.now())
    text = Column(String(500))


class GrowSession(Model):
    __tablename__ = 'grow_session'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    start_date = Column(Date)
    light_switch = Column(Date)
    end_date = Column(Date)

    day_start_hour = Column(Integer, default=6)
    night_start_hour = Column(Integer, default=24)

    brand = Column(String(50))
    num_plants = Column(Integer)
    square_centimeters = Column(Integer)
    gram_yield = Column(Integer)

    light_devices = relationship('LightDevice', back_populates='grow_session')
    water_devices = relationship('WaterDevice', back_populates='grow_session')
    flower_devices = relationship('FlowerDevice', back_populates='grow_session')
    flower_data = relationship('FlowerData', back_populates='grow_session')
    subscribers = relationship('Subscriber', back_populates='grow_session')

    def __repr__(self):
        return self.name

    def is_active(self):
        return self.start_date is not None and self.end_date is None

    @staticmethod
    def get_active():
        result = []
        for grow_session in appbuilder.session.query(GrowSession).all():
            if grow_session.is_active():
                result.append(grow_session)
        return result


class LightDevice(Model):
    __tablename__ = 'light_device'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    key = Column(String(5), nullable=False)
    device = Column(Integer, nullable=False)

    state = Column(Boolean, default=False)

    grow_session_id = Column(Integer, ForeignKey('grow_session.id'))
    grow_session = relationship("GrowSession")

    def __repr__(self):
        return self.name

    @staticmethod
    def get_active():
        result = []
        for light_device in appbuilder.session.query(LightDevice).all():
            if light_device.grow_session.is_active():
                result.append(light_device)
        return result


class WaterDevice(Model):
    __tablename__ = 'water_device'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    key = Column(String(5), nullable=False)
    device = Column(Integer, nullable=False)

    switch_off_time = Column(DateTime)

    water_threshhold = Column(REAL, default=25)
    watering_duration_minutes = Column(Integer, default=20)

    grow_session_id = Column(Integer, ForeignKey('grow_session.id'))
    grow_session = relationship("GrowSession")

    def __repr__(self):
        return self.name

    def state(self):
        return self.switch_off_time is not None

    @staticmethod
    def get_turned_on():
        result = []
        for water_device in appbuilder.session.query(WaterDevice).all():
            if water_device.state():
                result.append(water_device)
        return result


class FlowerDevice(Model):
    __tablename__ = 'flower_device'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    mac = Column(String(50), nullable=False)

    grow_session_id = Column(Integer, ForeignKey('grow_session.id'))
    grow_session = relationship('GrowSession')

    flower_data = relationship('FlowerData',
                               back_populates='flower_device',
                               order_by='desc(FlowerData.timestamp)')

    def __repr__(self):
        return self.name


class FlowerData(Model):
    __tablename__ = 'flower_data'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True, default=func.now())
    temperature = Column(REAL)
    light = Column(Integer)
    water = Column(REAL)
    battery = Column(Integer)
    ecb = Column(REAL)
    ec_porus = Column(REAL)
    dli = Column(REAL)
    ea = Column(REAL)

    flower_device_id = Column(Integer, ForeignKey('flower_device.id'), nullable=False)
    flower_device = relationship('FlowerDevice')

    grow_session_id = Column(Integer, ForeignKey('grow_session.id'), nullable=False)
    grow_session = relationship('GrowSession')

    def get_data_dict(self):
        return dict(
            TimeStamp=str(self.timestamp),
            Temperature=str(self.temperature),
            Light=str(self.light),
            Water=str(self.water),
            Battery=str(self.battery),
            ecb=str(self.ecb),
            ec_porus=str(self.ec_porus),
            dli=str(self.dli),
            ea=str(self.ea)
        )

    @staticmethod
    def new_flower_data(data, flower_device_id, grow_session_id):
        return FlowerData(
            temperature=data['Temperature'],
            light=data['Light'],
            water=data['Water'],
            battery=data['Battery'],
            ecb=data['Ecb'],
            ec_porus=data['EcPorus'],
            dli=data['DLI'],
            ea=data['Ea'],
            flower_device_id=flower_device_id,
            grow_session_id=grow_session_id,
        )


class Subscriber(Model):
    __tablename__ = 'subscriber'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    receiver_email = Column(String)

    grow_session_id = Column(Integer, ForeignKey('grow_session.id'))
    grow_session = relationship("GrowSession")

    def __repr__(self):
        return self.name

    @staticmethod
    def get_active_subscribers():
        result = []
        for subscriber in appbuilder.session.query(Subscriber).all():
            if subscriber.grow_session.is_active():
                result.append(subscriber)
        return result
