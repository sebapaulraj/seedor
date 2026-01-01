from pydantic import BaseModel, ConfigDict, EmailStr, constr
from typing import List, Optional
from app.db.consentmodel import Consent
from app.db.notification import Notification


base_model_config = ConfigDict(
    arbitrary_types_allowed=True,
    from_attributes=True
)

#---------- ConsentRequest New -------------#
class NotificationModel(BaseModel):
    idnotification: str
    senderIdUser: str
    senderSeedorId: str
    receiverIdUser: str
    receiverSeedorId: str
    itemType: str
    notificationType: str
    templateCode: str
    deliveryMethod: str
    messageTitle: str
    messageSubject: str
    messagebody: str
    deliveryStatus: str
    readingStatus: str   
    createdDate: Optional[str] = None   
    status: str = None

class NotificationRequestNewIN(BaseModel):
    senderSeedorId: str   
    receiverSeedorId: str
    itemType: str= None
    notificationType: str
    templateCode: str= None
    deliveryMethod: str
    messageTitle: str
    messageSubject: str
    messagebody: str= None   
    attributes: dict = None   

class NotificationRequestIN(BaseModel):
    idnotification: str
    deliveryStatus: str
    readingStatus: str

class NotificationOut(BaseModel):
    listnotification: List[NotificationModel]
    statuscode : str 
    statusmessage: str
   
class Config:
    orm_mode = True
    from_attributes = True
