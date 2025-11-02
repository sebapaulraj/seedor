import uuid
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    iduser = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)
    name = Column(String(150), nullable=True)
    email = Column(String(250), unique=True, nullable=False, index=True)
    password = Column(String(70), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())



class Profile(Base):
    __tablename__ = "profile"

    idprofile = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)
    authIduser=Column(String(45), nullable=False)
    seedorId = Column(String(100), nullable=False)
    isValidSeedorId=Column(Boolean,nullable=False)
    preferedName = Column(String(150), nullable=False)
    firstName = Column(String(100), nullable=True)
    middleName = Column(String(100), nullable=True)
    lastName = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(100), nullable=True)
    countryCode= Column(String(100), nullable=True)
    countryName= Column(String(200), nullable=True)
    isPhoneVerified= Column(Boolean, default=False, nullable=False)
    profileType=Column(String(45), nullable=True)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())

class ResetPassword(Base):
    __tablename__ = "resetpassword"

    idResetPassword = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)
    idUser=Column(String(45), nullable=False)
    password = Column(String(100), nullable=False)
    verifyURL= Column(String(300), nullable=False)
    isActivated= Column(Boolean, nullable=False)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())