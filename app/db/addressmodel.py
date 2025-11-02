import uuid
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.db.models import Base

class Address(Base):
    __tablename__ = "address"

    idaddress = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)
    idUser=Column(String(45), nullable=False)    
    addressId = Column(String(100), nullable=False)
    isActive= Column(Boolean, nullable=False)
    label= Column(String(100), nullable=False)
    primaryAddress= Column(Boolean, nullable=False)
    street=Column(String(250), nullable=False)
    area=Column(String(250), nullable=False)
    city=Column(String(250), nullable=False)
    stateorProvince=Column(String(100), nullable=False)
    postalCode=Column(String(45), nullable=False)
    country=Column(String(100), nullable=False)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())
