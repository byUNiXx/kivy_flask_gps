import enum
import re
import string

from sqlalchemy.orm import validates, relationship

from extensions import db
from models.base import BaseModel


class Types(enum.Enum):
    car = 'car'
    bike = 'bike'
    truck = 'truck'
    skate = 'skate'
    other_heavy = 'other_heavy'
    other_light = 'other_light'


class Phone(BaseModel):
    __tablename__ = 'phone'
    pid = db.Column(db.CHAR(36), primary_key=True)

    moving = relationship("Moving", uselist=False, back_populates="phone", cascade="all, delete-orphan")

    alarms = relationship("PhoneAlarm", cascade="all, delete-orphan", back_populates="phone")

    def __init__(self, pid):
        self.pid = pid

    def serialize(self):
        return {"pid": self.pid}


class Moving(BaseModel):
    __tablename__ = 'moving'
    pid = db.Column(db.CHAR(36), db.ForeignKey(Phone.pid), primary_key=True)
    ip = db.Column(db.VARCHAR(36), nullable=False)
    type = db.Column(db.Enum(Types), nullable=False)
    utc = db.Column(db.VARCHAR(6), nullable=False)

    lat = db.Column(db.DECIMAL(9, 6), nullable=True)
    lon = db.Column(db.DECIMAL(9, 6), nullable=True)
    alt = db.Column(db.DECIMAL(9, 3), nullable=True)
    timestamp = db.Column(db.DateTime(), nullable=True)

    phone = relationship("Phone", back_populates="moving")

    def __init__(self, pid, ip, _type, utc, lat, lon, alt, timestamp):
        self.pid = pid
        self.ip = ip
        self.type = _type
        self.utc = utc
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.timestamp = timestamp

    def serialize(self):
        return {"pid": self.pid,
                "ip": self.ip,
                "type": self.type.name,
                "utc": self.utc,
                "lat": float(self.lat) if self.lat is not None else None,
                "lon": float(self.lon) if self.lon is not None else None,
                "alt": float(self.alt) if self.lon is not None else None,
                "timestamp": re.sub('[-:+]', '',
                                    self.timestamp.isoformat()) + 'Z' if self.timestamp is not None else None}

    @validates('lat')
    def validate_lat(self, key, value):
        if value is None:
            return value
        if value < -90 or value > 90:
            raise ValueError('Latitud invalida')
        return value

    @validates('lon')
    def validate_lon(self, key, value):
        if value is None:
            return value
        if value < -180 or value > 180:
            raise ValueError('Longitud invalida')
        return value

    @validates('pid')
    def validate_pid(self, key, value):
        check = string.hexdigits + '-'
        split: str = value.split('-')

        if len(split) != 5:
            raise ValueError("Invalid PID")

        if len(split[0]) != 8 or len(split[1]) != 4 or len(split[2]) != 4 or len(split[3]) != 4 or len(split[4]) != 12:
            raise ValueError("Invalid PID")

        for letter in value:
            if letter not in check:
                raise ValueError("Invalid PID")

        print("Llega a return value")
        return value

    # @validates('UTC')
    # def validate_utc(self, key, value):
    #     if value is None:
    #         return value
    #     if value
