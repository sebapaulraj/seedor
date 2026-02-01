import os
import json
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.db.accessmodel import Access
from app.db.consentmodel import ConsentRequest,Consent
from app.db.db import get_db, engine
from app.db.addressmodel import Address
from app.db.usermodel import Profile
from app.db.agreementmodel import Agreement
from app.db.shipmentmodel import Shipment
from app.db.models import Base
from app.schemas.consentschema import ConsentModel, ConsentRequestNewIN, ConsentGetIN,ConsentGetOUT, ConsentRequestOut
from app.api.consentrequest import validateConsentItem


# def createConsentRequest(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
#     # ensure unique email (handled by DB unique constraint but check to return friendly message)
#     userId=payload["userid"] #Item Baneficiary
#     profileId=payload["profileId"]
#     email=payload["email"]    
    
#     response_data=ConsentRequestOut(
#         idconsentrequest="",
#         itemOwnerIdUser ="",
#         itemBeneficiaryIdUser ="",
#         itemType="",
#         itemId="",
#         status="",
#         requestedBy="",
#         requestedTo="",        
#         isactiveConnection=False,
#         consentSendStatus="User Not Online",
#         statuscode="ERROR",
#         statusmessage="Invalid Consent Request Object"  
#     )  
     
#     validateConsentItem(consentReq_in, db)

#     profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemOwnerSeedorId).first()
#     if not profile:
#         response_data.statuscode="ERROR"
#         response_data.statusmessage="Invalid Consent Request Seedorid"
#         return response_data 
             
#     tmp_accessCount=db.query(func.max(Access.seqCounter)).filter(
#         Access.accessTypeId == consentReq_in.itemId).filter(
#         Access.accessTypeValue == consentReq_in.itemType).filter(
#         Access.idUser==profile.authIduser).scalar() 
        
#     if not tmp_accessCount:
#         response_data.statuscode="ERROR"
#         response_data.statusmessage="Access not defined for the Item"
#         return response_data 
     
#     tmpAccess=db.query(Access).filter(
#         Access.accessTypeId == consentReq_in.itemId).filter(
#         Access.accessTypeValue == consentReq_in.itemType).filter(
#         Access.idUser==profile.authIduser).filter(Access.seqCounter==tmp_accessCount).first()
    
#     if not tmpAccess or tmpAccess.accessStatus!="PUBLIC":
#         response_data.statuscode="ERROR"
#         response_data.statusmessage="Item has restricted access!"
#         return response_data  

#     tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
#         ConsentRequest.itemOwnerIdUser == userId).filter(
#         ConsentRequest.itemBeneficiaryIdUser == profile.authIduser).filter(
#         ConsentRequest.itemId==consentReq_in.itemId).scalar()  
      
#     if not tmp_seq or  tmp_seq==0:
#         tmp_seq=1
#     else:
#         tmp_seq=tmp_seq+1
    
#     new_consentRequest=ConsentRequest(
#         itemOwnerIdUser =profile.authIduser ,    
#         itemBeneficiaryIdUser = userId,
#         itemType=consentReq_in.itemType,
#         itemId=consentReq_in.itemId,  
#         status="REQUEST",
#         seqCounter=tmp_seq,
#         requestedBy=userId,
#         requestedTo=profile.authIduser,
#         createdBy =userId,
#         updatedBy = userId        
#     )  
        
#     try:
#         db.add(new_consentRequest)
#         db.commit()
#         db.refresh(new_consentRequest) 
#         response_data.idconsentrequest=new_consentRequest.idconsentrequest
#         response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
#         response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
#         response_data.itemType=new_consentRequest.itemType
#         response_data.itemId=new_consentRequest.itemId
#         response_data.status=new_consentRequest.status
#         response_data.requestedBy=new_consentRequest.requestedBy
#         response_data.requestedTo=new_consentRequest.requestedTo
#         response_data.statuscode="SUCCESS"
#         response_data.statusmessage="Consent Request Raised Successfully"
    
#     except IntegrityError as e:            
#         db.rollback()
#         raise HTTPException(status_code=400, detail="Consent Request Failed")        

#     return response_data

# def createConsentOffer(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
#     # ensure unique email (handled by DB unique constraint but check to return friendly message)
#     userId=payload["userid"]
#     profileId=payload["profileId"]
#     email=payload["email"]    
    
#     response_data=ConsentRequestOut(
#         idconsentrequest="",
#         itemOwnerIdUser="",  
#         itemBeneficiaryIdUser="",
#         itemType="",
#         itemId="",
#         status="",
#         requestedBy="",
#         requestedTo="",       
#         isactiveConnection=False,
#         consentSendStatus="User Not Online",       
#         statuscode="ERROR",
#         statusmessage="Invalid Consent Request Object"  
#     )  

#     validateConsentItem(consentReq_in, db)

#     profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemBeneficiarySeedorId).first()
#     if not profile:
#         response_data.statusmessage="Invalid Beneficiry Seedorid"
#         return response_data
    
#     tmp_accessCount=db.query(func.max(Access.seqCounter)).filter(
#         Access.accessTypeId == consentReq_in.itemId).filter(
#         Access.accessTypeValue == consentReq_in.itemType).filter(
#         Access.idUser==userId).scalar() 
    
#     if not tmp_accessCount:
#        response_data.statusmessage="Item has private access!"
#        return response_data
     
#     tmpAccess=db.query(Access).filter(
#         Access.accessTypeId == consentReq_in.itemId).filter(
#         Access.accessTypeValue == consentReq_in.itemType).filter(
#         Access.idUser==userId).filter(Access.seqCounter==tmp_accessCount).first()
    
#     if not tmpAccess or tmpAccess.accessStatus!="PUBLIC":
#         response_data.statusmessage="Item has private access"
#         return response_data 
    
#     tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
#         ConsentRequest.itemBeneficiaryIdUser == profile.authIduser ).filter(
#         ConsentRequest.itemOwnerIdUser == userId).filter(
#         ConsentRequest.itemId==consentReq_in.itemId).scalar()  
      
#     if not tmp_seq or  tmp_seq==0:
#         tmp_seq=1
#     else:
#         tmp_seq=tmp_seq+1
    
#     new_consentRequest=ConsentRequest(
#         itemOwnerIdUser=userId ,    
#         itemBeneficiaryIdUser = profile.authIduser,
#         itemType=consentReq_in.itemType,
#         itemId=consentReq_in.itemId,  
#         status="REQUEST",
#         seqCounter=tmp_seq,
#         requestedBy=userId,
#         requestedTo=profile.authIduser,
#         createdBy =userId,
#         updatedBy = userId        
#     )  
        
#     try:
#         db.add(new_consentRequest)
#         db.commit()
#         db.refresh(new_consentRequest) 
#         response_data.idconsentrequest=new_consentRequest.idconsentrequest
#         response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
#         response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
#         response_data.itemType=new_consentRequest.itemType
#         response_data.itemId=new_consentRequest.itemId
#         response_data.status=new_consentRequest.status       
#         response_data.statuscode="SUCCESS"
#         response_data.statusmessage="Consent Request Raised Successfully"
    
#     except IntegrityError as e:            
#         db.rollback()
#         raise HTTPException(status_code=400, detail="Consent Request Failed")        

#     return response_data

# def acceptConsentRequest(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
#     # ensure unique email (handled by DB unique constraint but check to return friendly message)
#     userId=payload["userid"]
#     profileId=payload["profileId"]
#     email=payload["email"]    
    
#     response_data=ConsentRequestOut(
#         idconsentrequest="",
#         itemOwnerIdUser="",  
#         itemBeneficiaryIdUser="",
#         itemType="",
#         itemId="",
#         status="",
#         requestedBy="",
#         requestedTo="",
#         isactiveConnection=False,
#         consentSendStatus="User not Active",        
#         statuscode="ERROR",
#         statusmessage="Invalid Consent Request Object"  
#         )
    
         
#     validateConsentItem(consentReq_in, db)
#     profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemOwnerSeedorId).first()
#     if not profile:
#         response_data.statusmessage="Invalid Beneficiary Seedorid"
#         return response_data
    
#     tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
#         ConsentRequest.itemOwnerIdUser ==  profile.authIduser).filter(
#         ConsentRequest.itemBeneficiaryIdUser == userId  ).filter(
#         ConsentRequest.itemId==consentReq_in.itemId).scalar()    
#     if not tmp_seq or tmp_seq==0:
#         tmp_seq=1
#     else:
#         tmp_seq=tmp_seq+1
    
#     new_consentRequest=ConsentRequest(
#         itemOwnerIdUser=profile.authIduser ,    
#         itemBeneficiaryIdUser = userId,
#         itemType=consentReq_in.itemType,  
#         itemId=consentReq_in.itemId,  
#         status="ACCEPT",
#         seqCounter=tmp_seq,
#         requestedBy=userId,
#         requestedTo=profile.authIduser,
#         createdBy =userId,
#         updatedBy = userId        
#     ) 
              
#     try:        
#         db.add(new_consentRequest)
#        # db.add(new_consent)
#         db.commit()
#         db.refresh(new_consentRequest) 
#         response_data.idconsentrequest=new_consentRequest.idconsentrequest
#         response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
#         response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
#         response_data.itemId=new_consentRequest.itemId
#         response_data.itemType=new_consentRequest.itemType
#         response_data.status=new_consentRequest.status            
#         response_data.statuscode="SUCCESS"
#         response_data.statusmessage="Consent Grand Successfully"


#     except IntegrityError as e:            
#         db.rollback()
#         raise HTTPException(status_code=400, detail="Consent Grand Failed")        

#     return response_data


# def acceptConsentOffer(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
#     # ensure unique email (handled by DB unique constraint but check to return friendly message)
#     userId=payload["userid"]
#     profileId=payload["profileId"]
#     email=payload["email"]    
    
#     response_data=ConsentRequestOut(
#         idconsentrequest="",
#         itemOwnerIdUser="",  
#         itemBeneficiaryIdUser="",
#         itemType="",
#         itemId="",
#         status="",       
#         requestedBy="",
#         requestedTo="",
#         isactiveConnection=False,
#         consentSendStatus="User not Active",
#         updatedDate="",
#         statuscode="ERROR",
#         statusmessage="Invalid consent Object"  
#         )
    
         
#     validateConsentItem(consentReq_in, db)
#     profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemBeneficiarySeedorId).first()
#     if not profile:
#         raise HTTPException(status_code=400, detail="Invalid Signatory Seedorid") 
    
#     tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
#         ConsentRequest.itemOwnerIdUser == userId ).filter(
#         ConsentRequest.itemBeneficiaryIdUser == profile.authIduser ).filter(
#         ConsentRequest.itemId==consentReq_in.itemId).scalar()    
#     if not tmp_seq or tmp_seq==0:
#         tmp_seq=1
#     else:
#         tmp_seq=tmp_seq+1
    
#     new_consentRequest=ConsentRequest(
#         itemOwnerIdUser = userId,    
#         itemBeneficiaryIdUser = profile.authIduser ,
#         itemType=consentReq_in.itemType,  
#         itemId=consentReq_in.itemId,  
#         status="ACCEPT",
#         seqCounter=tmp_seq,
#         requestedBy=userId,
#         requestedTo=profile.authIduser,
#         createdBy =userId,
#         updatedBy = userId        
#     ) 
              
#     try:        
#         db.add(new_consentRequest)
#        # db.add(new_consent)
#         db.commit()
#         db.refresh(new_consentRequest) 
#         response_data.idconsentrequest=new_consentRequest.idconsentrequest
#         response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
#         response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
#         response_data.itemId=new_consentRequest.itemId
#         response_data.status=new_consentRequest.status              
#         response_data.statuscode="SUCCESS"
#         response_data.statusmessage="Consent Grand Successfully"


#     except IntegrityError as e:            
#         db.rollback()
#         raise HTTPException(status_code=400, detail="Consent Grand Failed")        

#     return response_data


# def rejectConsentRequest(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
#     # ensure unique email (handled by DB unique constraint but check to return friendly message)
#     userId=payload["userid"]
#     profileId=payload["profileId"]
#     email=payload["email"]    
    
#     response_data=ConsentRequestOut(
#         idconsentrequest="",
#         itemOwnerIdUser="",  
#         itemBeneficiaryIdUser="",
#         itemType="",
#         itemId="",
#         status="",
#         requestedBy="",
#         requestedTo="",
#         isactiveConnection=False,
#         consentSendStatus="User not Active",      
#         statuscode="ERROR",
#         statusmessage="Invalid consent Object"  
#         )
    
    
#     validateConsentItem(consentReq_in, db)
#     profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemOwnerSeedorId).first()
#     if not profile:
#         raise HTTPException(status_code=400, detail="Invalid Item Owner Seedorid") 
    
#     tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
#         ConsentRequest.itemOwnerIdUser ==profile.authIduser ).filter(
#         ConsentRequest.itemBeneficiaryIdUser == userId).filter(
#         ConsentRequest.itemId==consentReq_in.itemId).scalar()    
#     if tmp_seq==0:
#         tmp_seq=1
#     else:
#         tmp_seq=tmp_seq+1
    
#     new_consentRequest=ConsentRequest(
#         itemOwnerIdUser=userId,    
#         itemBeneficiaryIdUser = profile.authIduser,
#         itemType=consentReq_in.itemType,  
#         itemId=consentReq_in.itemId,  
#         status="REJECT",
#         seqCounter=tmp_seq,
#         requestedBy=userId,
#         requestedTo=profile.authIduser,
#         updatedBy = userId,
#         createdBy =userId       
#     ) 
   
#     try:        
#         db.add(new_consentRequest)  
#         db.commit()      
#         db.refresh(new_consentRequest) 
#         response_data.idconsentrequest=new_consentRequest.idconsentrequest
#         response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
#         response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
#         response_data.itemId=new_consentRequest.itemId
#         response_data.status=new_consentRequest.status       
#         response_data.statuscode="SUCCESS"
#         response_data.statusmessage="Consent REVOKED Successfully"

#     except IntegrityError as e:            
#         db.rollback()
#         raise HTTPException(status_code=400, detail="Consent Grand Successfully")        

#     return response_data


# def rejectConsentOffer(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
#     # ensure unique email (handled by DB unique constraint but check to return friendly message)
#     userId=payload["userid"]
#     profileId=payload["profileId"]
#     email=payload["email"]    
    
#     response_data=ConsentRequestOut(
#         idconsentrequest="",
#         itemOwnerIdUser="",  
#         itemBeneficiaryIdUser="",
#         itemType="",
#         itemId="",
#         status="",
#         requestedBy="",
#         requestedTo="",
#         isactiveConnection=False,
#         consentSendStatus="User not Active",
#         statuscode="ERROR",
#         statusmessage="Invalid Consent Request Object"  
#         )
    
    
#     validateConsentItem(consentReq_in, db)
#     profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemBeneficiarySeedorId).first()
#     if not profile:
#         raise HTTPException(status_code=400, detail="Invalid Signatory Seedorid") 
    
#     tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
#         ConsentRequest.itemOwnerIdUser ==userId ).filter(
#         ConsentRequest.itemBeneficiaryIdUser ==  profile.authIduser).filter(
#         ConsentRequest.itemId==consentReq_in.itemId).scalar()    
#     if tmp_seq==0:
#         tmp_seq=1
#     else:
#         tmp_seq=tmp_seq+1
    
#     new_consentRequest=ConsentRequest(
#         itemOwnerIdUser=profile.authIduser ,    
#         itemBeneficiaryIdUser = userId,
#         itemType=consentReq_in.itemType,  
#         itemId=consentReq_in.itemId,  
#         status="REJECT",
#         seqCounter=tmp_seq,
#         requestedBy=userId,
#         requestedTo=profile.authIduser,
#         updatedBy = userId,
#         createdBy =userId       
#     ) 
   
#     try:        
#         db.add(new_consentRequest)  
#         db.commit()      
#         db.refresh(new_consentRequest) 
#         response_data.idconsentrequest=new_consentRequest.idconsentrequest
#         response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
#         response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
#         response_data.itemId=new_consentRequest.itemId
#         response_data.status=new_consentRequest.status        
#         response_data.statuscode="SUCCESS"
#         response_data.statusmessage="Consent REVOKED Successfully"

#     except IntegrityError as e:            
#         db.rollback()
#         raise HTTPException(status_code=400, detail="Consent Grand Successfully")        

#     return response_data

# '''
# def getConsentOfferd(payload: dict,consent_in: ConsentGetIN, request: Request, db: Session = Depends(get_db)):
#     userId=payload["userid"]
#     profileId=payload["profileId"]
#     email=payload["email"]    
   

#     consent_listOut=ConsentGetOUT(
#         idconsent="",
#         listConsent=[],
#         statuscode="ERROR",
#         statusmessage="No Address Found" 
#         )

#     if consent_in.idconsent :
#         tmp_consent = db.query(Consent).filter(Consent.idconsent == consent_in.idconsent).first()
#         consent_listOut.listConsent.append(tmp_consent)
#         consent_listOut.statuscode="SUCCESS"
#         consent_listOut.statusmessage="Address Found" 
#     else:
#         consent_list=db.query(Consent).filter(Consent.itemOwnerSeedorId == userId).all()
#         for tmpconsent in consent_list: 
#             tmpconsentBaseModel=ConsentModel(
#                 itemOwnerIdUser= tmpconsent.itemOwnerIdUser,
#                 itemBeneficiaryIdUser=tmpconsent.itemBeneficiaryIdUser,
#                 itemOwnerSeedorId=tmpconsent.itemOwnerSeedorId, 
#                 signatorySeedorId=tmpconsent.itemBeneficiarySeedorId,
#                 itemType=tmpconsent.itemType,
#                 itemId=tmpconsent.itemId,
#                 status=tmpconsent.status,
#                 grantedOn=tmpconsent.grantedOn,
#                 validUntil=tmpconsent.validUntil
#             )           
#             consent_listOut.listConsent.append(tmpconsentBaseModel)
#         consent_listOut.statuscode="SUCCESS"
#         consent_listOut.statusmessage="Address Found" 

#     response_data=consent_listOut

#     return response_data
# '''

def getConsentOfferdId(payload: dict,consent_in: ConsentGetIN,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    consent_listOut=ConsentGetOUT(
        listConsent=[],
        statuscode="ERROR",
        statusmessage="No Consent Found" 
        )

    consent_list=db.query(Consent).filter(Consent.itemId == consent_in.itemId).filter(
        Consent.itemOwnerIdUser==userId).order_by(Consent.updatedDate.desc()).all()
    
    for tmpconsent in consent_list: 
        tmpconsentBaseModel=ConsentModel(
            itemOwnerIdUser= tmpconsent.itemOwnerIdUser,
            itemBeneficiaryIdUser=tmpconsent.itemBeneficiaryIdUser,
            itemOwnerSeedorId=tmpconsent.itemOwnerSeedorId, 
            itemBeneficiarySeedorId=tmpconsent.itemBeneficiarySeedorId,
            itemType=tmpconsent.itemType,
            itemId=tmpconsent.itemId,
            status=tmpconsent.status,
            grantedOn=str(tmpconsent.grantedOn),
            revokedOn=str(tmpconsent.revokedOn),
            validUntil=str(tmpconsent.validUntil)
        )           
        consent_listOut.listConsent.append(tmpconsentBaseModel)
    consent_listOut.statuscode="SUCCESS"
    consent_listOut.statusmessage="Consent Found" 

    response_data=consent_listOut

    return response_data

def getConsentOfferdAll(payload: dict,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    consent_listOut=ConsentGetOUT(
        idconsent="",
        listConsent=[],
        statuscode="ERROR",
        statusmessage="No Consent Found" 
        )

    consent_list=db.query(Consent).filter(Consent.itemOwnerIdUser == userId).order_by(Consent.updatedDate.desc()).all()
    for tmpconsent in consent_list: 
        tmpconsentBaseModel=ConsentModel(
            itemOwnerIdUser= tmpconsent.itemOwnerIdUser,
            itemBeneficiaryIdUser=tmpconsent.itemBeneficiaryIdUser,
            itemOwnerSeedorId=tmpconsent.itemOwnerSeedorId, 
            itemBeneficiarySeedorId=tmpconsent.itemBeneficiarySeedorId,
            itemType=tmpconsent.itemType,
            itemId=tmpconsent.itemId,
            status=tmpconsent.status,
            grantedOn=str(tmpconsent.grantedOn),
            revokedOn=str(tmpconsent.revokedOn),
            validUntil=str(tmpconsent.validUntil)
        )           
        consent_listOut.listConsent.append(tmpconsentBaseModel)
    consent_listOut.statuscode="SUCCESS"
    consent_listOut.statusmessage="Address Found" 

    response_data=consent_listOut

    return response_data
'''
def getConsentSigned(payload: dict,consent_in: ConsentGetIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    consent_listOut=ConsentGetOUT(
        idconsent="",
        listConsent=[],
        statuscode="ERROR",
        statusmessage="No Consent Found" 
        )

    if consent_in.idconsent :
        tmp_consent = db.query(Consent).filter(Consent.idconsent == consent_in.idconsent).first()
        consent_listOut.listConsent.append(tmp_consent)
        consent_listOut.statuscode="SUCCESS"
        consent_listOut.statusmessage="Consent Found" 
    else:
        consent_list=db.query(Consent).filter(Consent.itemBeneficiaryIdUser == userId).all()
        for tmpconsent in consent_list: 
            tmpconsentBaseModel=ConsentModel(
                itemOwnerIdUser= tmpconsent.itemOwnerIdUser,
                itemBeneficiaryIdUser=tmpconsent.itemBeneficiaryIdUser,
                itemOwnerSeedorId=tmpconsent.itemOwnerSeedorId, 
                itemBeneficiarySeedorId=tmpconsent.itemBeneficiarySeedorId,
                itemType=tmpconsent.itemType,
                itemId=tmpconsent.itemId,
                status=tmpconsent.status,
                grantedOn=tmpconsent.grantedOn,
                validUntil=tmpconsent.validUntil
            )           
            consent_listOut.listConsent.append(tmpconsentBaseModel)
        consent_listOut.statuscode="SUCCESS"
        consent_listOut.statusmessage="Consent Found" 

    response_data=consent_listOut

    return response_data
'''
def getConsentSignedId(payload: dict,consent_in: ConsentGetIN,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    consent_listOut=ConsentGetOUT(
        listConsent=[],
        statuscode="ERROR",
        statusmessage="No Consent Found" 
        )

    consent_list=db.query(Consent).filter(Consent.itemId == consent_in.itemId).filter(
        Consent.itemBeneficiaryIdUser==userId).order_by(Consent.itemId,Consent.updatedDate.desc()).all()
    
    for tmpconsent in consent_list: 
        tmpconsentBaseModel=ConsentModel(
            itemOwnerIdUser= tmpconsent.itemOwnerIdUser,
            itemBeneficiaryIdUser=tmpconsent.itemBeneficiaryIdUser,
            itemOwnerSeedorId=tmpconsent.itemOwnerSeedorId, 
            itemBeneficiarySeedorId=tmpconsent.itemBeneficiarySeedorId,
            itemType=tmpconsent.itemType,
            itemId=tmpconsent.itemId,
            status=tmpconsent.status,
            grantedOn=str(tmpconsent.grantedOn),
            revokedOn=str(tmpconsent.revokedOn),
            validUntil=str(tmpconsent.validUntil)
        )           
        consent_listOut.listConsent.append(tmpconsentBaseModel)
    consent_listOut.statuscode="SUCCESS"
    consent_listOut.statusmessage="Consent Found" 

    response_data=consent_listOut

    return response_data

def getConsentSignedAll(payload: dict,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    consent_listOut=ConsentGetOUT(
        idconsent="",
        listConsent=[],
        statuscode="ERROR",
        statusmessage="No Consent Found" 
        )

    consent_list=db.query(Consent).filter(Consent.itemBeneficiaryIdUser == userId).order_by(Consent.itemId,Consent.updatedDate.desc()).all()
    for tmpconsent in consent_list: 
        tmpconsentBaseModel=ConsentModel(
            itemOwnerIdUser= tmpconsent.itemOwnerIdUser,
            itemBeneficiaryIdUser=tmpconsent.itemBeneficiaryIdUser,
            itemOwnerSeedorId=tmpconsent.itemOwnerSeedorId, 
            itemBeneficiarySeedorId=tmpconsent.itemBeneficiarySeedorId,
            itemType=tmpconsent.itemType,
            itemId=tmpconsent.itemId,
            status=tmpconsent.status,
            grantedOn=str(tmpconsent.grantedOn),
            revokedOn=str(tmpconsent.revokedOn),
            validUntil=str(tmpconsent.validUntil)
        )           
        consent_listOut.listConsent.append(tmpconsentBaseModel)
    consent_listOut.statuscode="SUCCESS"
    consent_listOut.statusmessage="Consent Found" 

    response_data=consent_listOut

    return response_data

