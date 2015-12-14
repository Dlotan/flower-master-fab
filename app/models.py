from flask.ext.appbuilder import Model
from flask.ext.appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, \
    String, ForeignKey, DateTime, \
    Boolean, REAL, Date, BLOB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import appbuilder, db, app
from datetime import datetime


def new_event(text):
    if not app.config['TESTING']:
        print("[" + str(datetime.now()) + "] " + text)
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
    night_start_hour = Column(Integer, default=0)

    brand = Column(String(50))
    num_plants = Column(Integer)
    square_centimeters = Column(Integer)
    gram_yield = Column(Integer)

    light_devices = relationship('LightDevice', back_populates='grow_session')
    water_devices = relationship('WaterDevice', back_populates='grow_session')
    flower_devices = relationship('FlowerDevice', back_populates='grow_session')
    flower_data = relationship('FlowerData', back_populates='grow_session')
    subscribers = relationship('Subscriber', back_populates='grow_session')
    webcams = relationship('Webcam', back_populates='grow_session')

    def __repr__(self):
        return self.name

    def is_active(self):
        """ Returns if the start_date exists => the GrowSession is active.

        Returns:
            bool: Active / Not Active.
        """
        return self.start_date is not None and self.end_date is None

    def is_day(self):
        """

        Returns:
            bool:
        """
        now = datetime.now()
        if self.night_start_hour < self.day_start_hour:  # Day -> 8:00 Night 1:00.
            if self.night_start_hour <= now.hour < self.day_start_hour:
                return False
            else:
                return True
        else:  # Day -> 8:00 Night 23:00.
            if self.day_start_hour <= now.hour < self.night_start_hour:
                return True
            else:
                return False

    def is_night(self):
        """

        Returns:
            bool:
        """
        return not self.is_day()

    @staticmethod
    def get_active():
        """ Get all GrowSessions which have a start_date
        Returns:
            list[GrowSession]:
        """
        result = []
        for grow_session in appbuilder.session.query(GrowSession).all():
            if grow_session.is_active():
                result.append(grow_session)
        return result

    @staticmethod
    def get_inactive():
        """ Get all GrowSessions which don't have a start_date
        Returns:
            list[GrowSession]:
        """
        result = []
        for grow_session in appbuilder.session.query(GrowSession).all():
            if not grow_session.is_active():
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

    def is_active(self):
        """

        Returns:
            bool: Active / Not Active.
        """
        if self.grow_session:
            if self.grow_session.is_active():
                return True
        return False

    @staticmethod
    def get_active():
        """ Get all LightDevices which have a GrowSession which is active
        Returns:
            list[LightDevice]:
        """
        result = []
        for light_device in appbuilder.session.query(LightDevice).all():
            if light_device.is_active():
                result.append(light_device)
        return result

    @staticmethod
    def get_inactive():
        """ Get all LightDevices which don't have a GrowSession which is active
        Returns:
            list[LightDevice]:
        """
        result = []
        for light_device in appbuilder.session.query(LightDevice).all():
            if not light_device.is_active():
                result.append(light_device)
        return result


class WaterDevice(Model):
    __tablename__ = 'water_device'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    key = Column(String(5), nullable=False)
    device = Column(Integer, nullable=False)

    switch_off_time = Column(DateTime)

    water_threshhold = Column(REAL, default=18)
    watering_duration_minutes = Column(Integer, default=30)

    grow_session_id = Column(Integer, ForeignKey('grow_session.id'))
    grow_session = relationship("GrowSession")

    def __repr__(self):
        return self.name

    def state(self):
        """ Returns if the WaterDevice is on right now.

        Returns:
            bool: On/Off.
        """
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
        """ Gets the FlowerData as dict of strings.
        Returns:
            dict[str, str]:
        """
        return dict(
            TimeStamp=str(self.timestamp),
            Temperature=str(self.temperature),
            Light=str(self.light),
            Water=str(self.water),
            Battery=str(self.battery),
            Ecb=str(self.ecb),
            EcPorus=str(self.ec_porus),
            DLI=str(self.dli),
            Ea=str(self.ea)
        )

    @staticmethod
    def new_flower_data(data, flower_device_id, grow_session_id):
        """

        Args:
            data (dict[str, T]):
            flower_device_id (str):
            grow_session_id (str):

        Returns:
            FlowerData:
        """
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

    def is_active(self):
        """

        Returns:
            bool: Aktive / Not Aktive
        """
        if self.grow_session:
            if self.grow_session.is_active():
                return True
        return False

    @staticmethod
    def get_active():
        """ Get Subscribers which have active GrowSession.
        Returns:
            list[Subscriber]: List of all active Subscribers.
        """
        result = []
        for subscriber in appbuilder.session.query(Subscriber).all():
            if subscriber.is_active():
                result.append(subscriber)
        return result


class Webcam(Model):
    __tablename = 'webcam'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    devicepath = Column(String)

    webcam_screenshots = relationship('WebcamScreenshot', back_populates='webcam')

    grow_session_id = Column(Integer, ForeignKey('grow_session.id'))
    grow_session = relationship("GrowSession")

    def __repr__(self):
        return self.name

    def is_active(self):
        """

        Returns:
            bool: Aktive / Not Aktive
        """
        if self.grow_session:
            if self.grow_session.is_active():
                return True
        return False

    @staticmethod
    def get_active():
        """

        Returns:
            list[Webcam]: List of all active Webcams.
        """
        result = []
        for webcam in appbuilder.session.query(Webcam).all():
            if webcam.is_active():
                result.append(webcam)
        return result


class WebcamScreenshot(Model):
    __tablename__ = 'webcam_screenshot'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True, default=func.now())
    file = Column(BLOB)
    sizex = Column(Integer)
    sizey = Column(Integer)

    webcam_id = Column(Integer, ForeignKey('webcam.id'))
    webcam = relationship("Webcam")

    def get_size(self):
        return self.sizex, self.sizey

    @staticmethod
    def new_webcam_screenshot(image, webcam):
        return WebcamScreenshot(
            file=image.tobytes(),
            sizex=image.size[0],
            sizey=image.size[1],
            webcam_id=webcam.id,
        )
