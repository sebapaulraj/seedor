from pydantic import BaseModel, ConfigDict, EmailStr, constr
from typing import List, Optional
from app.db.consentmodel import Consent


base_model_config = ConfigDict(
    arbitrary_types_allowed=True,
    from_attributes=True
)

#---------- ConsentRequest New -------------#
class ConsentModel(BaseModel):
    offerorIdUser:str  
    signatoryIdUser:str
    offerorSeedorId:str
    signatorySeedorId:str
    itemType:str
    itemId:str   
    status:str 
    grantedOn:str
    revokedOn:str
   
class ConsentRequestNewIN(BaseModel):
    offerorSeedorId : str 
    signatorySeedorId : str 
    itemType: str
    itemId:str

class ConsentRequestOut(BaseModel):
    idconsentrequest:str
    offerorIdUser:str  
    signatoryIdUser:str
    itemType: str
    itemId:str
    status:str
    isactiveConnection:bool
    consentSendStatus:str
    updatedDate:str   
    statuscode:str
    statusmessage:str 
   
#---------- ConsentRequest End -------------#


#---------- Consent -------------#

class ConsentNewIN(BaseModel):
    offerorSeedorId : str 
    signatorySeedorId : str 
    itemType: str
    itemId:str
    status:str    
    isActive:bool

class ConsentOut(BaseModel):
    idconsentrequest:str
    offerorIdUser:str  
    signatoryIdUser:str
    isActive:bool
    statuscode:str
    statusmessage:str 

 
class ConsentUpdateIN(BaseModel):
    idconsent:str
    isActive:str
    
class ConsentGetIN(BaseModel):
    idconsent:str
   
class ConsentGetOUT(BaseModel):   
    listConsent:List[ConsentModel]
    statuscode:str
    statusmessage:str
   

class Config:
    orm_mode = True
    from_attributes = True
