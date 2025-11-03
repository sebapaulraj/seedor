from pydantic import BaseModel, ConfigDict, EmailStr, constr
from typing import List, Optional
from app.db.accessmodel import Access
from app.db.agreementmodel import Agreement
from app.db.shipmentmodel import Shipment,Shipmenttracking
from app.db.addressmodel import Address

base_model_config = ConfigDict(
    arbitrary_types_allowed=True,
    from_attributes=True
)

#---------- User -------------#

class UserCreate(BaseModel):
    name: constr(max_length=120) | None = None
    email: EmailStr
    password: constr(min_length=8, max_length=72)
    

class UserOut(BaseModel):
    iduser: str  
    is_active: bool
    statuscode:str
    statusmessage:str

class UserName(BaseModel):
    email: EmailStr

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

#---------- User Profile -------------#

class UserProfile(BaseModel): 
    seedorId :str
    preferedName:str 
    firstName : str
    middleName : str   
    lastName : str 
    phone :str 
    countryCode: str 
    countryName:str   
    profileType:str

class UserProfileOut(BaseModel):
    idprofile: str
    statuscode:str
    statusmessage:str

#---------- Validate Seedor -------------#

class ValidateSeedorId(BaseModel):
    seedorId :str

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
    

class AddressNewIN(BaseModel):
    label:str
    street:str
    area:str
    city:str
    stateorProvince:str
    postalCode:str
    country:str

class AddressOut(BaseModel):
    idaddress:str
    addressId:str
    isActive:bool
    statuscode:str
    statusmessage:str 

class AddressUpdateIN(BaseModel):
    idaddress:str
    label:str
    primaryAddress:bool

class AddressDeleteIN(BaseModel):
    idaddress:str
   

class AddressGetIN(BaseModel):
    addressId:str
   
class AddressGetOUT(BaseModel):
    listAddress:List[AddressBase]
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
    accessTypeId : str
    accessTypeValue: str 
    
    
class AccessOut(BaseModel):
    idaccess:str
    accessStatus:str
    seqCounter:int
    statuscode:str
    statusmessage:str 

class AccessGetIdIN(BaseModel):
    idaccess:str

class AccessGetIdTypeIN(BaseModel):
    accessTypeId:str  
    
class AccessGetIN(BaseModel):
    idaccess:str
   
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
    label : str
    title: str 
    summary : str 
    content : str 
    details: str

class AgreementOut(BaseModel):
    idagreement:str
    isActive:bool
    statuscode:str
    statusmessage:str 

class AgreementUpdateIN(BaseModel):
    idagreement:str
    label: str
    title: str
    summary: str
    content:str  
    details:str
    

class AgreementDeleteIN(BaseModel):
    idagreement:str

class AgreementGetIN(BaseModel):
    agreementId:str
   
class AgreementGetOUT(BaseModel):
    listAgreement:List[AgreementBase]
    statuscode:str
    statusmessage:str
    

#----------Shipment -------------#

class ShipmentBase(BaseModel):
    shipmentCode:str  
    idUser : str
    label : str
    shipperId:str
    shipperName:str
    description:str
    isActive:bool
   
class ShipmentNewIN(BaseModel):
    shipmentCode : str
    idUser: str 
    label : str 
    shipperId:str
    shipperName : str 
    description: str
    isActive:bool    

class ShipmentOut(BaseModel):
    idshipment:str
    isActive:bool
    statuscode:str
    statusmessage:str 

class ShipmentUpdateIN(BaseModel):
    idshipment:str
    isActive:str
    
class ShipmentGetIN(BaseModel):
    shipmentCode:str
   
class ShipmentGetOUT(BaseModel):
    listShipment:List[ShipmentBase]
    statuscode:str
    statusmessage:str
  

#----------Shipment Tracking-------------#

class ShipmenttrackingBase(BaseModel):
    idshipmenttracking:str  
    idUserSeedorId:str 
    shipmentCode :str
    shipmentTransitCode:str
    shipmentTransitTitle:str
    shipmenttrackingcontent:str
    shipmentTransitSummary:str
    shipmentTransitDetail:str
    isActive:bool
    seqNumber:int
      

class ShipmenttrackingNewIN(BaseModel):   
    userSeedorid : str 
    shipmentTransitCode : str 
    shipmentTransitTitle: str
    shipmenttrackingcontent: str
    shipmentTransitSummary: str
    shipmentTransitDetail: str
        

class ShipmenttrackingOut(BaseModel):
    idshipmenttracking:str
    shipmentCode:str
    isActive:bool
    statuscode:str
    statusmessage:str 

class ShipmenttrackingUpdateIN(BaseModel):
    shipmentCode:str
    userSeedorid : str 
    shipmentTransitCode : str 
    shipmentTransitTitle: str
    shipmenttrackingcontent: str
    shipmentTransitSummary: str
    shipmentTransitDetail: str
    isActive:str
    
class ShipmenttrackingGetIN(BaseModel):
    shipmentCode:str
   
class ShipmenttrackingGetOUT(BaseModel):
    shipmentCode:str
    listShipmenttracking:List[ShipmenttrackingBase]
    statuscode:str
    statusmessage:str
  

class Config:
    orm_mode = True
    from_attributes = True
