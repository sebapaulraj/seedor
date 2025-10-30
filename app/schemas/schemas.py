from pydantic import BaseModel, ConfigDict, EmailStr, constr
from typing import List, Optional
from app.db.models import Address,Access,Agreement,Consent,Shipment,Shipmenttracking

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
    idaddress:str
   
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
    idaccess:str
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
    idagreement:str
   
class AgreementGetOUT(BaseModel):
    listAgreement:List[AgreementBase]
    statuscode:str
    statusmessage:str
    
#---------- Consent -------------#

class ConsentNewIN(BaseModel):
    offerorIdUser : str
    signatoryIdUser: str 
    offerorSeedorId : str 
    signatorySeedorId : str 
    itemType: str
    itemId:str
    status:str    
    isActive:bool

class ConsentOut(BaseModel):
    idconsent:str
    isActive:bool
    statuscode:str
    statusmessage:str 

class ConsentUpdateIN(BaseModel):
    idconsent:str
    isActive:str
    
class ConsentGetIN(BaseModel):
    idconsent:str
   
class ConsentGetOUT(BaseModel):
    idconsent:str
    listConsent:List[Consent]
    statuscode:str
    statusmessage:str
    model_config = base_model_config

#----------Shipment -------------#

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
    idshipment:str
   
class ShipmentGetOUT(BaseModel):
    idshipment:str
    listShipment:List[Shipment]
    statuscode:str
    statusmessage:str
    model_config = base_model_config

#----------Shipment Tracking-------------#

class ShipmenttrackingNewIN(BaseModel):
    idshipment : str
    idstatusUser: str 
    shipmentCode : str 
    shipmentTransitCode : str 
    shipmentTransitTitle: str
    shipmenttrackingcontent: str
    shipmentTransitSummary: str
    shipmentTransitDetail: str
    isActive:bool    

class ShipmenttrackingOut(BaseModel):
    idshipmenttracking:str
    isActive:bool
    statuscode:str
    statusmessage:str 

class ShipmenttrackingUpdateIN(BaseModel):
    idshipmenttracking:str
    isActive:str
    
class ShipmenttrackingGetIN(BaseModel):
    idshipmenttracking:str
   
class ShipmenttrackingGetOUT(BaseModel):
    idshipmenttracking:str
    listShipmenttracking:List[Shipmenttracking]
    statuscode:str
    statusmessage:str
    model_config = base_model_config



class Config:
    orm_mode = True
    from_attributes = True
