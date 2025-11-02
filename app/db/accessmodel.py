import uuid
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.db.models import Base

class Access(Base):
    __tablename__ = "access"

    idaccess = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)    
    idUser=Column(String(45), nullable=False)    
    accessTypeId = Column(String(100), nullable=False)
    accessTypeValue= Column(String(100), nullable=False)
    accessGrantedOn= Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())
    accessStatus=Column(String(100), nullable=False)  
    seqCounter= Column(Integer, nullable=False)  
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())