import uuid
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.db.models import Base

Base = declarative_base()

class Consent(Base):
    __tablename__ = "consent"

    idconsent = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)    
    itemOwnerIdUser=Column(String(45), nullable=False)    
    itemBeneficiaryIdUser = Column(String(100), nullable=False)
    itemOwnerSeedorId= Column(String(100), nullable=False)
    itemBeneficiarySeedorId= Column(String(100), nullable=False)
    itemType= Column(String(100), nullable=True)
    itemId=Column(String(100), nullable=True)    
    status=Column(String(100), nullable=True)  
    grantedOn=Column(String, nullable=True)
    revokedOn=Column(String, nullable=True)
    validUntil=Column(String, nullable=True)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())

class ConsentRequest(Base):
    __tablename__ = "consentrequest"

    idconsentrequest = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)    
    itemOwnerIdUser=Column(String(45), nullable=False)    
    itemBeneficiaryIdUser = Column(String(100), nullable=False)
    itemType= Column(String(100), nullable=False)
    itemId=Column(String(100), nullable=False)    
    status=Column(String(100), nullable=False)  
    seqCounter=Column(Integer, nullable=False)
    consentValididtyFrequency=Column(String(100), nullable=True)
    requestedBy=Column(Integer, nullable=False)
    requestedTo=Column(Integer, nullable=False)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())