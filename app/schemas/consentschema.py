from pydantic import BaseModel, ConfigDict, EmailStr, constr
from typing import List, Optional
from app.db.consentmodel import Consent


base_model_config = ConfigDict(
    arbitrary_types_allowed=True,
    from_attributes=True
)

#---------- ConsentRequest New -------------#
class ConsentModel(BaseModel):
    itemOwnerIdUser:str  
    itemBeneficiaryIdUser:str
    itemOwnerSeedorId:str
    itemBeneficiarySeedorId:str
    itemType:str
    itemId:str   
    status:str 
    grantedOn: Optional[str] = None
    revokedOn: Optional[str] = None
    validUntil: Optional[str] = None
    
   
class ConsentRequestNewIN(BaseModel):
    itemOwnerSeedorId : str 
    itemBeneficiarySeedorId : str 
    itemType: str
    itemId:str
    consentValididtyFrequency:str

class ConsentRequest(BaseModel):
    idconsentrequest:str
    itemOwnerIdUser:str  
    itemBeneficiaryIdUser:str
    itemType: str
    itemId:str
    status:str
    consentValididtyFrequency:str
    requestedBy:str
    requestedTo:str
    seqCounter:int

class ConsentRequestOut(BaseModel):
    idconsentrequest:str
    itemOwnerIdUser:str  
    itemOwnerSeedorId:str
    itemBeneficiaryIdUser:str
    itemBeneficiarySeedor:str
    itemType: str
    itemId:str
    status:str
    consentValididtyFrequency:str
    requestedBy:str
    requestedTo:str
    seqCounter:int
    isactiveConnection:bool
    consentSendStatus:str   
    statuscode:str
    statusmessage:str 


class ConsentRequestGETIN(BaseModel):   
    itemType: str
    itemId:str
      
class ConsentRequestallOUT(BaseModel):   
    listConsentRequest:List[ConsentRequest]
    statuscode:str
    statusmessage:str
#---------- ConsentRequest End -------------#


#---------- Consent -------------#

class ConsentNewIN(BaseModel):
    itemOwnerSeedorId : str 
    itemBeneficiarySeedorId : str 
    itemType: str
    itemId:str
    status:str    
    isActive:bool

class ConsentOut(BaseModel):
    idconsentrequest:str
    itemOwnerSeedorId : str 
    itemBeneficiarySeedorId : str 
    isActive:bool    
    statuscode:str
    statusmessage:str 

 
class ConsentUpdateIN(BaseModel):
    idconsent:str
    isActive:str
    
class ConsentGetIN(BaseModel):
    itemId:str
   
class ConsentGetOUT(BaseModel):   
    listConsent:List[ConsentModel]
    statuscode:str
    statusmessage:str
   

class Config:
    orm_mode = True
    from_attributes = True
