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


class Consent(Base):
    __tablename__ = "consent"

    idconsent = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)    
    offerorIdUser=Column(String(45), nullable=False)    
    signatoryIdUser = Column(String(100), nullable=False)
    offerorSeedorId= Column(String(100), nullable=False)
    signatorySeedorId= Column(String(100), nullable=False)
    itemType= Column(String(100), nullable=True)
    itemId=Column(String(100), nullable=True)    
    status=Column(String(100), nullable=True)  
    grantedOn=Column(Boolean, nullable=False,onupdate=func.now())
    isActive=Column(Boolean, nullable=False)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())


class Shipment(Base):
    __tablename__ = "shipment"

    idshipment = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)    
    shipmentCode=Column(String(45), nullable=False)    
    idUser = Column(String(100), nullable=False)
    label= Column(String(100), nullable=False)
    shipperId=Column(String(100), nullable=False)
    shipperName= Column(String(100), nullable=True)
    description= Column(String(1000), nullable=True)
    isActive=Column(Boolean, nullable=False)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())




class Shipmenttracking(Base):
    __tablename__ = "shipmenttracking"

    idshipmenttracking = Column(String(45), primary_key=True, index=True,default=lambda: str(uuid.uuid4()), unique=True)    
    idshipment=Column(String(45), nullable=False)    
    shipmentCode = Column(String(100), nullable=False)
    shipmentTransitCode= Column(String(100), nullable=False)
    shipmentTransitTitle= Column(String(100), nullable=True)
    shipmenttrackingcontent= Column(String(100), nullable=True)
    shipmentTransitSummary= Column(String(100), nullable=True)
    shipmentTransitDetail= Column(String(1000), nullable=True)
    isActive=Column(Boolean, nullable=False)
    createdBy = Column(String(45),default='SEEDOR',nullable=False)
    createdDate = Column(DateTime,default=datetime.now, nullable=False)
    updatedBy = Column(String(45), default='SEEDOR', nullable=False)
    updatedDate = Column(DateTime,default=datetime.now, nullable=False,onupdate=func.now())