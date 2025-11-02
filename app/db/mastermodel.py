import uuid
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.db.models import Base


class Lov(Base):
    __tablename__ = "lov"

    idlov = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)
    lovCode=Column(String(100), nullable=False)
    lovKey = Column(String(100), nullable=False)
    lovValue = Column(String(100), nullable=False)
    lovAttribute1 = Column(String(100), nullable=True)
    lovAttribute2 = Column(String(100), nullable=True)
    lovAttribute3 = Column(String(100), nullable=True)
    lovAttribute4 = Column(String(100), nullable=True)
    lovAttribute5 = Column(String(100), nullable=True)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())