import re

from sqlalchemy.orm import relationship

from extensions import db
from models.base import BaseModel


class PhoneAlarm(BaseModel):
    __tablename__ = "phone_alarm"

    phone_id = db.Column(db.CHAR(36), db.ForeignKey("phone.pid"), primary_key=True)
    alarm_id = db.Column(db.Integer, db.ForeignKey("alarm.aid"), primary_key=True)
    timestamp = db.Column(db.DateTime(), nullable=True)
    status = db.Column(db.BOOLEAN, nullable=True)

    alarm = relationship("Alarm", back_populates="phones")
    phone = relationship("Phone", back_populates="alarms")

    def serialize(self):
        return {"pid": self.phone_id,
                "aid": self.alarm_id,
                "status": self.status,
                "timestamp": re.sub('[-:+]', '',
                                    self.timestamp.isoformat()) + 'Z' if self.timestamp is not None else None}
