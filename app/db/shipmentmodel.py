import uuid
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from app.db.models import Base


class Shipment(Base):
    __tablename__ = "shipment"

    idshipment = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)    
    shipmentCode=Column(String(45), nullable=False)    
    agencyId = Column(String(100), nullable=False)
    label= Column(String(100), nullable=False)
    shipperId=Column(String(100), nullable=False)
    shipperName= Column(String(100), nullable=True)
    deliveryId= Column(String(100), default='SEEDOR', nullable=True)
    description= Column(String(1000), nullable=True)
    isActive=Column(Boolean, nullable=False)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())




class Shipmenttracking(Base):
    __tablename__ = "shipmenttracking"

    idshipmenttracking = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)    
    idshipment=Column(String(45), nullable=True)   
    idUserSeedorId=Column(String(45), nullable=True) 
    idUser=Column(String(45), nullable=True) 
    idstatusUser= Column(String(45), nullable=True) 
    shipmentCode = Column(String(100), nullable=True)
    shipmentTransitCode= Column(String(100), nullable=False)
    shipmentTransitTitle= Column(String(100), nullable=True)
    shipmenttrackingcontent= Column(String(100), nullable=True)
    shipmentTransitSummary= Column(String(100), nullable=True)
    shipmentTransitDetail= Column(String(1000), nullable=True)
    isActive=Column(Boolean, nullable=False)
    seqNumber=Column(Integer, nullable=True)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())