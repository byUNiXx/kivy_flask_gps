from sqlalchemy.orm import relationship

from extensions import db
from models.base import BaseModel


class Alarm(BaseModel):
    __tablename__ = 'alarm'

    aid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(15), nullable=False)
    description = db.Column(db.VARCHAR(1024), nullable=True)

    phones = relationship("PhoneAlarm", back_populates="alarm")

    def __init__(self, name):
        self.name = name

    def serialize(self):
        return {"aid": self.aid,
                "name": self.name,
                "description": self.description if self.description is not None else None}
