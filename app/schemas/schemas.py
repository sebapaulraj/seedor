from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, constr, Field
from typing import List, Optional
from app.db.accessmodel import Access
from app.db.agreementmodel import Agreement
from app.db.shipmentmodel import Shipment,Shipmenttracking
from app.db.addressmodel import Address

base_model_config = ConfigDict(
    arbitrary_types_allowed=True,
    from_attributes=True
)

#---------- WebSocket Message -------------#

class PushMessage(BaseModel):
    actor_id: str
    message: str

#---------- User -------------#

class UserCreate(BaseModel):
    name: constr(min_length=3, max_length=120) 
    email: EmailStr
    password: constr(min_length=8, max_length=72)
    

class UserOut(BaseModel):
    iduser: str  
    is_active: bool
    statuscode:str
    statusmessage:str

class UserName(BaseModel):
    email: EmailStr

class Password(BaseModel):
    password: str
    

class UserNameOut(BaseModel):
    email: str
    is_active: bool
    statuscode:str
    statusmessage:str

#---------- Login -------------#

class LoginUser(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=72)

class LoginOut(BaseModel):
    idprofile : str
    authIduser:str
    seedorId :str
    isValidSeedorId:bool
    preferedName : str
    firstName : str
    middleName : str
    lastName : str
    email :str
    phone : str
    countryCode:str 
    countryName:str 
    isPhoneVerified:bool
    profileType:str    
    statuscode:str
    statusmessage:str

#---------- Lov -------------#
   
class LovListItem(BaseModel):
    lovKey: str
    lovValue: str
    lovAttribute1: Optional[str] = None
    lovAttribute2: Optional[str] = None
    lovAttribute3: Optional[str] = None
    lovAttribute4: Optional[str] = None
    lovAttribute5: Optional[str] = None

class LovOut(BaseModel):
    idlov: str
    lovCode: str
    lovlist: List[LovListItem]
    statuscode:str
    statusmessage:str

class LovIn(BaseModel):
    lovCode: str

class LovAddressIn(BaseModel):
    country_code: str
    postal_code: str

class MasterDataInsertOut(BaseModel): 
    inserted:str
    skipped: str
    total:int
    

#---------- User Profile -------------#

class UserProfile(BaseModel): 
    seedorId: str = Field(min_length=3)
    preferedName: str = Field(min_length=3)
    firstName: str = Field(min_length=3)
    middleName: str = Field(min_length=0)
    lastName: str = Field(min_length=3)
    phone: str = Field(min_length=0)
    countryCode: str = Field(min_length=3)
    countryName: str = Field(min_length=3)
    profileType: str = Field(min_length=3)

class UserProfileOut(BaseModel):
    idprofile: str
    statuscode:str
    statusmessage:str

#---------- Validate Seedor -------------#

class ValidateSeedorId(BaseModel):
    seedorId: str =Field(min_length=3)

class ValidateSeedorIdOut(BaseModel):
    seedorIdAvaiable:bool
    statuscode:str
    statusmessage:str  

#---------- Reset Password -------------#

class ResetPassword(BaseModel): 
    idResetPassword :str 
    idUser:str
    password : str
    verifyURL : str   
    isActivated : bool 

class ResetPasswordOut(BaseModel): 
    idResetPassword :str
    isActivated : bool
    statuscode:str
    statusmessage:str  

class EmailOut(BaseModel): 
    statuscode:str
    statusmessage:str  

#----------Address -------------# 
class AddressBase(BaseModel):
    idaddress : str 
    addressId : str
    isActive: bool
    label: str
    primaryAddress: bool
    street:str
    area:str
    city:str
    postalCode:str
    country:str

class AddressBaseOut(BaseModel):
    idaddress : str 
    addressId : str
    isActive: bool
    label: str
    primaryAddress: bool
    street:str
    area:str
    city:str
    postalCode:str
    country:str
    access:str
    

class AddressNewIN(BaseModel):
    label:str =Field(min_length=3, max_length=100)
    street:str =Field(min_length=3, max_length=250)
    area:str =Field(min_length=0, max_length=250)
    city:str =Field(min_length=3, max_length=250)
    stateorProvince:str =Field(min_length=3, max_length=100)
    postalCode:str =Field(min_length=0, max_length=45)
    country:str =Field(min_length=3, max_length=100)

class AddressOut(BaseModel):
    idaddress:str
    addressId:str
    isActive:bool
    statuscode:str
    statusmessage:str 

class AddressUpdateIN(BaseModel):
    idaddress:str =Field(min_length=3, max_length=45)
    label:str =Field(min_length=3, max_length=45)
    primaryAddress:bool =Field(...)

class AddressDeleteIN(BaseModel):
    idaddress:str  =Field(min_length=3, max_length=45)
   

class AddressGetIN(BaseModel):
    addressId:str =Field(min_length=3, max_length=45)
   
class AddressGetOUT(BaseModel):
    listAddress:List[AddressBaseOut]
    statuscode:str
    statusmessage:str
   
#----------Access -------------#

class AccessBase(BaseModel):
    idaccess :str    
    idUser:str    
    accessTypeId :str
    accessTypeValue:str
    accessGrantedOn:str
    accessStatus:str
    seqCounter:int

class AccessNewIN(BaseModel):
    accessTypeId : str  =Field(min_length=3, max_length=45)
    accessTypeValue: str   =Field(min_length=3, max_length=250)
    
    
class AccessOut(BaseModel):
    idaccess:str
    accessStatus:str
    seqCounter:int
    statuscode:str
    statusmessage:str 

class AccessGetIdIN(BaseModel):
    idaccess:str =Field(min_length=3, max_length=45)

class AccessGetIdTypeIN(BaseModel):
    accessTypeId:str   =Field(min_length=3, max_length=45)
    

class AccessGetIdTypePublicIN(BaseModel):
    accessTypeValue:str   =Field(min_length=3, max_length=250)
    seedorId:str   =Field(min_length=3, max_length=250)
    
class AccessGetIN(BaseModel):
    idaccess:str =Field(min_length=3, max_length=45)
   
class AccessGetOUT(BaseModel):
    listAccess:List[AccessBase]
    statuscode:str
    statusmessage:str
   

#----------Agreement -------------#

class AgreementBase(BaseModel):
    idagreement:str
    agreementId:str  
    label: str
    title: str
    summary: str
    content:str  
    details:str
    isActive:bool
   

class AgreementNewIN(BaseModel):
    label : str =Field(min_length=3, max_length=100)
    title: str  =Field(min_length=3, max_length=100)
    summary : str  =Field(min_length=0, max_length=1000)
    content : str  =Field(min_length=0, max_length=5000)
    details: str =Field(min_length=3, max_length=5000)

class AgreementOut(BaseModel):
    idagreement:str
    agreementId:str
    isActive:bool
    statuscode:str
    statusmessage:str 

class AgreementUpdateIN(BaseModel):
    agreementId:str =Field(min_length=3, max_length=45)
    label: str =Field(min_length=3, max_length=100)
    title: str  =Field(min_length=3, max_length=100)
    summary : str  =Field(min_length=0, max_length=1000)
    content : str  =Field(min_length=0, max_length=5000)
    details: str =Field(min_length=3, max_length=5000)
    

class AgreementDeleteIN(BaseModel):
    idagreement:str =Field(min_length=3, max_length=45)

class AgreementGetIN(BaseModel):
    agreementId:str =Field(min_length=3, max_length=45)
   
class AgreementGetOUT(BaseModel):
    listAgreement:List[AgreementBase]
    statuscode:str
    statusmessage:str
    

#----------Shipment -------------#

class ShipmentBase(BaseModel):
    idshipment:str
    shipmentCode:str 
    agencyId : str 
    agencyId : str
    label : str
    shipperId:str
    shipperName:str
    description:str
    deliveryId:str
    isActive:bool
    createdDate:datetime


class ShipmentNewIN(BaseModel):
    agencySeedorId:str
    deliverySeedorId:str 
    description: str =Field(min_length=3)
       

class ShipmentOut(BaseModel):
    idshipment:str
    shipmentCode:str
    isActive:bool
    createdDate:datetime 
    statuscode:str
    statusmessage:str
    

class ShipmentUpdateIN(BaseModel):
    idshipment:str =Field(min_length=3, max_length=45)
    agencySeedorId:str 
    deliverySeedorId:str 
    description: str 

class ShipmentGetIN(BaseModel):
    shipmentCode:str =Field(min_length=3, max_length=45)
   
class ShipmentGetOUT(BaseModel):
    listShipment:List[ShipmentBase]
    statuscode:str
    statusmessage:str
  

#----------Shipment Tracking-------------#

class ShipmenttrackingBase(BaseModel):
    idshipmenttracking:str   
    idUserSeedorId:str 
    shipmentCode :str
    deliverySeedorId:str
    shipmentTransitCode:str
    shipmentTransitTitle:str
    shipmenttrackingcontent:str
    shipmentTransitSummary:str
    shipmentTransitDetail:str
    isActive:bool
    seqNumber:int
    createdDate:datetime
    deliverySeedorId:str  
      

class ShipmenttrackingNewIN(BaseModel):   
    userSeedorid : str  =Field(min_length=3, max_length=100)   
    shipmentTransitCode : str  =Field(min_length=3, max_length=250)
    shipmentTransitTitle: str =Field(min_length=3, max_length=100)
    shipmenttrackingcontent: str =Field(min_length=3, max_length=1000)
    shipmentTransitSummary: str =Field(min_length=0, max_length=500)
    shipmentTransitDetail: str =Field(min_length=0, max_length=2500)
    deliverySeedorId:str =Field(min_length=3, max_length=100)
        

class ShipmenttrackingOut(BaseModel):
    idshipmenttracking:str
    shipmentCode:str
    isActive:bool
    createdDate:datetime 
    statuscode:str
    statusmessage:str 

class ShipmenttrackingUpdateIN(BaseModel):
    shipmentCode:str =Field(min_length=3, max_length=45)
    userSeedorid : str =Field(min_length=3, max_length=100)
    deliverySeedorId:str =Field(min_length=3, max_length=100)
    shipmentTransitCode : str  =Field(min_length=3, max_length=250)
    shipmentTransitTitle: str =Field(min_length=3, max_length=100)
    shipmenttrackingcontent: str =Field(min_length=3, max_length=1000)
    shipmentTransitSummary: str =Field(min_length=0, max_length=500)
    shipmentTransitDetail: str =Field(min_length=0, max_length=2500)
    isActive:str=Field(...)
    deliverySeedorId:str =Field(min_length=3, max_length=100)
    
class ShipmenttrackingGetIN(BaseModel):
    shipmentCode:str =Field(min_length=3, max_length=45)
   
class ShipmenttrackingGetOUT(BaseModel):
    shipmentCode:str
    listShipmenttracking:List[ShipmenttrackingBase]
    statuscode:str
    statusmessage:str
  

class Config:
    orm_mode = True
    from_attributes = True
