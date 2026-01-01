import uuid
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.db.models import Base

Base = declarative_base()

class Notification(Base):
    __tablename__ = "notification"

    idnotification= Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True) 
    senderIdUser= Column(String(45), nullable=False)
    senderSeedorId= Column(String(45), nullable=False)
    receiverIdUser= Column(String(45), nullable=False)
    receiverSeedorId= Column(String(45), nullable=False)
    itemType= Column(String(100), nullable=True)
    notificationType= Column(String(100), nullable=True)
    templateCode= Column(String(100), nullable=True)
    deliveryMethod= Column(String(100), nullable=True)
    messageTitle= Column(String(100), nullable=True)
    messageSubject= Column(String(100), nullable=True)
    messagebody= Column(String(100), nullable=True)
    deliveryStatus= Column(String(100), nullable=True)
    readingStatus= Column(String(100), nullable=True)
    attributes= Column(String(3000), nullable=True)
    createdBy= Column(String(45),default='SEEDOR',nullable=False)
    createdDate= Column(DateTime,default=datetime.now, nullable=False)
    updatedBy= Column(String(45),default='SEEDOR',nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())
    status= Column(String(100), nullable=True)

