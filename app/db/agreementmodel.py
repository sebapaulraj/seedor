import uuid
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.db.models import Base


class Agreement(Base):
    __tablename__ = "agreement"

    idagreement = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)    
    agreementId=Column(String(45), nullable=False)    
    idUser = Column(String(100), nullable=False)
    label= Column(String(100), nullable=False)
    title= Column(String(100), nullable=False)
    summary= Column(String(100), nullable=True)
    content=Column(String(100), nullable=True)    
    details=Column(String(100), nullable=True)  
    isActive=Column(Boolean, nullable=False)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())

