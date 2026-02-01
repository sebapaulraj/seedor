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
from app.core.config import settings
from app.db.accessmodel import Access
from app.db.consentmodel import ConsentRequest,Consent
from app.db.db import get_db, engine
from app.db.addressmodel import Address
from app.db.usermodel import Profile
from app.db.agreementmodel import Agreement
from app.db.shipmentmodel import Shipment
from app.db.models import Base
from app.schemas.consentschema import ConsentModel, ConsentRequestGETIN, ConsentRequestNewIN, ConsentGetIN,ConsentGetOUT, ConsentRequestOut, ConsentRequestallOUT


def validateConsentItem(consentReq_in: ConsentRequestNewIN, db: Session = Depends(get_db)):
    item=None
    if consentReq_in.itemType=="ADDRESS":
        item = db.query(Address).filter(Address.idaddress == consentReq_in.itemId).first()

    if consentReq_in.itemType=="AGREEMENT":
        item = db.query(Agreement).filter(Agreement.idagreement == consentReq_in.itemId).first()

    if consentReq_in.itemType=="SHIPMENT":
        item = db.query(Shipment).filter(Shipment.idshipment == consentReq_in.itemId).first()
    
    if not item:
        raise HTTPException(status_code=400, detail="Invalid Item Type")     



def createConsentRequest(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"] #Item Baneficiary
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentRequestOut(
        idconsentrequest="",
        itemOwnerIdUser ="",
        itemOwnerSeedorId="",
        itemBeneficiaryIdUser ="",
        itemBeneficiarySeedor="",   
        itemType="",
        itemId="",
        status="",
        consentValididtyFrequency="",
        requestedBy="",
        requestedTo="", 
        seqCounter=0,       
        isactiveConnection=False,
        consentSendStatus="User Not Online",
        statuscode="ERROR",
        statusmessage="Invalid Consent Request Object"  
    )  
     
    validateConsentItem(consentReq_in, db)

    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemOwnerSeedorId).first()
    tmp_BeneficiaryProfile=db.query(Profile).filter(Profile.authIduser==userId).first()

    if not profile:
        response_data.statuscode="ERROR"
        response_data.statusmessage="Invalid Consent Request Seedorid"
        return response_data 
    
    if not tmp_BeneficiaryProfile:
        response_data.statuscode="ERROR"
        response_data.statusmessage="Invalid Beneficiary Userid"
        return response_data
             
    tmp_accessCount=db.query(func.max(Access.seqCounter)).filter(
        Access.accessTypeId == consentReq_in.itemId).filter(
        Access.accessTypeValue == consentReq_in.itemType).filter(
        Access.idUser==profile.authIduser).scalar() 
        
    if not tmp_accessCount:
        response_data.statuscode="ERROR"
        response_data.statusmessage="Access not defined for the Item"
        return response_data 
     
    tmpAccess=db.query(Access).filter(
        Access.accessTypeId == consentReq_in.itemId).filter(
        Access.accessTypeValue == consentReq_in.itemType).filter(
        Access.idUser==profile.authIduser).filter(Access.seqCounter==tmp_accessCount).first()
    
    if not tmpAccess or tmpAccess.accessStatus!="PUBLIC":
        response_data.statuscode="ERROR"
        response_data.statusmessage="Item has restricted access!"
        return response_data  

    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.itemOwnerIdUser == userId).filter(
        ConsentRequest.itemBeneficiaryIdUser == profile.authIduser).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()  
      
    tmp_seq = 1 if not tmp_seq or tmp_seq == 0 else tmp_seq + 1

    new_consentRequest=ConsentRequest(
        itemOwnerIdUser =profile.authIduser ,    
        itemBeneficiaryIdUser = userId,
        itemType=consentReq_in.itemType,
        itemId=consentReq_in.itemId,  
        status="REQUEST",
        consentValididtyFrequency=consentReq_in.consentValididtyFrequency,
        seqCounter=tmp_seq,
        requestedBy=userId,
        requestedTo=profile.authIduser,
        createdBy =userId,
        updatedBy = userId        
    )  
        
    try:
        db.add(new_consentRequest)
        db.commit()
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
        response_data.itemOwnerSeedorId=profile.seedorId
        response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
        response_data.itemBeneficiarySeedor=tmp_BeneficiaryProfile.seedorId
        response_data.itemType=new_consentRequest.itemType
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status
        response_data.consentValididtyFrequency=new_consentRequest.consentValididtyFrequency
        response_data.requestedBy=new_consentRequest.requestedBy
        response_data.requestedTo=new_consentRequest.requestedTo
        response_data.seqCounter=new_consentRequest.seqCounter
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Consent Request Raised Successfully"
    
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Consent Request Failed")        

    return response_data

def createConsentOffer(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentRequestOut(
        idconsentrequest="",
        itemOwnerIdUser="", 
        itemOwnerSeedorId=  "", 
        itemBeneficiaryIdUser="",
        itemBeneficiarySeedor="",
        itemType="",
        itemId="",
        status="",
        consentValididtyFrequency="",
        requestedBy="",
        requestedTo="",
        seqCounter=0,       
        isactiveConnection=False,
        consentSendStatus="User Not Online",       
        statuscode="ERROR",
        statusmessage="Invalid Consent Request Object"  
    )  

    validateConsentItem(consentReq_in, db)

    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemBeneficiarySeedorId).first()
    tmp_OwnerProfile=db.query(Profile).filter(Profile.authIduser==userId).first()
    if not profile:
        response_data.statusmessage="Invalid Beneficiry Seedorid"
        return response_data
    
    if not tmp_OwnerProfile:
        response_data.statusmessage="Invalid Owner Userid"
        return response_data

    tmp_accessCount=db.query(func.max(Access.seqCounter)).filter(
        Access.accessTypeId == consentReq_in.itemId).filter(
        Access.accessTypeValue == consentReq_in.itemType).filter(
        Access.idUser==userId).scalar() 
    
    if not tmp_accessCount:
       response_data.statusmessage="Item has private access!"
       return response_data
     
    tmpAccess=db.query(Access).filter(
        Access.accessTypeId == consentReq_in.itemId).filter(
        Access.accessTypeValue == consentReq_in.itemType).filter(
        Access.idUser==userId).filter(Access.seqCounter==tmp_accessCount).first()
    
    if not tmpAccess or tmpAccess.accessStatus!="PUBLIC":
        response_data.statusmessage="Item has private access"
        return response_data 
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.itemBeneficiaryIdUser == profile.authIduser ).filter(
        ConsentRequest.itemOwnerIdUser == userId).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()  
      
    tmp_seq = 1 if not tmp_seq or tmp_seq == 0 else tmp_seq + 1
    
    new_consentRequest=ConsentRequest(
        itemOwnerIdUser=userId ,    
        itemBeneficiaryIdUser = profile.authIduser,
        itemType=consentReq_in.itemType,
        itemId=consentReq_in.itemId,  
        status="REQUEST",
        consentValididtyFrequency=consentReq_in.consentValididtyFrequency,
        seqCounter=tmp_seq,
        requestedBy=userId,
        requestedTo=profile.authIduser,
        createdBy =userId,
        updatedBy = userId        
    )  
        
    try:
        db.add(new_consentRequest)
        db.commit()
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
        response_data.itemOwnerSeedorId=tmp_OwnerProfile.seedorId
        response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
        response_data.itemBeneficiarySeedor=profile.seedorId
        response_data.itemType=new_consentRequest.itemType
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status   
        response_data.consentValididtyFrequency=new_consentRequest.consentValididtyFrequency 
        response_data.requestedBy=new_consentRequest.requestedBy
        response_data.requestedTo=new_consentRequest.requestedTo 
        response_data.seqCounter=new_consentRequest.seqCounter 
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Consent Request Raised Successfully"
    
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Consent Request Failed")        

    return response_data

def acceptConsentRequest(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentRequestOut(
        idconsentrequest="",
        itemOwnerIdUser="",  
        itemOwnerSeedorId="",
        itemBeneficiaryIdUser="",
        itemBeneficiarySeedor="",
        itemType="",
        itemId="",
        status="",
        consentValididtyFrequency="",
        requestedBy="",
        requestedTo="",
        seqCounter=0,
        isactiveConnection=False,
        consentSendStatus="User not Active",        
        statuscode="ERROR",
        statusmessage="Invalid Consent Request Object"  
        )
    
         
    validateConsentItem(consentReq_in, db)
    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemOwnerSeedorId).first()
    tmp_OwnerProfile=db.query(Profile).filter(Profile.authIduser==userId).first()
    if not profile:
        response_data.statusmessage="Invalid Beneficiary Seedorid"
        return response_data
    
    if not tmp_OwnerProfile:
        response_data.statusmessage="Invalid Owner Userid"
        return response_data
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.itemOwnerIdUser ==  profile.authIduser).filter(
        ConsentRequest.itemBeneficiaryIdUser == userId  ).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()    
    
    tmp_seq = 1 if not tmp_seq or tmp_seq == 0 else tmp_seq + 1

    new_consentRequest=ConsentRequest(
        itemOwnerIdUser=profile.authIduser ,    
        itemBeneficiaryIdUser = userId,
        itemType=consentReq_in.itemType,  
        itemId=consentReq_in.itemId,  
        status="ACCEPT",
        consentValididtyFrequency=consentReq_in.consentValididtyFrequency,
        seqCounter=tmp_seq,
        requestedBy=userId,
        requestedTo=profile.authIduser,
        createdBy =userId,
        updatedBy = userId        
    ) 
              
    try:        
        db.add(new_consentRequest)
       # db.add(new_consent)
        db.commit()
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
        response_data.itemOwnerSeedorId=profile.seedorId
        response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
        response_data.itemBeneficiarySeedor=tmp_OwnerProfile.seedorId
        response_data.itemId=new_consentRequest.itemId
        response_data.itemType=new_consentRequest.itemType
        response_data.status=new_consentRequest.status
        response_data.requestedBy=new_consentRequest.requestedBy
        response_data.requestedTo=new_consentRequest.requestedTo
        response_data.seqCounter=new_consentRequest.seqCounter
        response_data.consentValididtyFrequency=new_consentRequest.consentValididtyFrequency            
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Consent Grand Successfully"


    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Consent Grand Failed")        

    return response_data


def acceptConsentOffer(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentRequestOut(
        idconsentrequest="",
        itemOwnerIdUser="", 
        itemOwnerSeedorId="", 
        itemBeneficiaryIdUser="",
        itemBeneficiarySeedor="",
        itemType="",
        itemId="",
        status="", 
        consentValididtyFrequency="",      
        requestedBy="",
        requestedTo="",
        seqCounter=0,
        isactiveConnection=False,
        consentSendStatus="User not Active",
        updatedDate="",
        statuscode="ERROR",
        statusmessage="Invalid consent Object"  
        )
    
         
    validateConsentItem(consentReq_in, db)
    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemBeneficiarySeedorId).first()
    tmp_Ownerprofile = db.query(Profile).filter(Profile.authIduser == userId).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Invalid Signatory Seedorid") 
    
    if not tmp_Ownerprofile:
        raise HTTPException(status_code=400, detail="Invalid Owner Seedorid")
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.itemOwnerIdUser == userId ).filter(
        ConsentRequest.itemBeneficiaryIdUser == profile.authIduser ).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()   
     
    tmp_seq = 1 if not tmp_seq or tmp_seq == 0 else tmp_seq + 1
    
    new_consentRequest=ConsentRequest(
        itemOwnerIdUser = userId,    
        itemBeneficiaryIdUser = profile.authIduser ,
        itemType=consentReq_in.itemType,  
        itemId=consentReq_in.itemId,  
        status="ACCEPT",
        consentValididtyFrequency=consentReq_in.consentValididtyFrequency,
        seqCounter=tmp_seq,
        requestedBy=userId,
        requestedTo=profile.authIduser,
        createdBy =userId,
        updatedBy = userId        
    ) 
              
    try:        
        db.add(new_consentRequest)
       # db.add(new_consent)
        db.commit()
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
        response_data.itemOwnerSeedorId=tmp_Ownerprofile.seedorId
        response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
        response_data.itemBeneficiarySeedor=profile.seedorId
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status
        response_data.requestedBy=new_consentRequest.requestedBy
        response_data.requestedTo=new_consentRequest.requestedTo
        response_data.seqCounter=new_consentRequest.seqCounter
        response_data.itemType=new_consentRequest.itemType
        response_data.consentValididtyFrequency=new_consentRequest.consentValididtyFrequency              
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Consent Grand Successfully"


    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Consent Grand Failed")        

    return response_data


def rejectConsentRequest(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentRequestOut(
        idconsentrequest="",
        itemOwnerIdUser="", 
        itemOwnerSeedorId="", 
        itemBeneficiaryIdUser="",
        itemBeneficiarySeedor="",
        itemType="",
        itemId="",
        status="",
        consentValididtyFrequency="",
        requestedBy="",
        requestedTo="",
        seqCounter=0,
        isactiveConnection=False,
        consentSendStatus="User not Active",      
        statuscode="ERROR",
        statusmessage="Invalid consent Object"  
        )
    
    
    validateConsentItem(consentReq_in, db)
    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemOwnerSeedorId).first()
    tmp_OwnerProfile = db.query(Profile).filter(Profile.authIduser == userId).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Invalid Item Owner Seedorid") 
    
    if not tmp_OwnerProfile:
        raise HTTPException(status_code=400, detail="Invalid Owner Seedorid")
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.itemOwnerIdUser ==profile.authIduser ).filter(
        ConsentRequest.itemBeneficiaryIdUser == userId).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar() 
       
    tmp_seq = 1 if not tmp_seq or tmp_seq == 0 else tmp_seq + 1
    
    new_consentRequest=ConsentRequest(
        itemOwnerIdUser=userId,    
        itemBeneficiaryIdUser = profile.authIduser,
        itemType=consentReq_in.itemType,  
        itemId=consentReq_in.itemId,  
        status="REJECT",
        consentValididtyFrequency=consentReq_in.consentValididtyFrequency,
        seqCounter=tmp_seq,
        requestedBy=userId,
        requestedTo=profile.authIduser,
        updatedBy = userId,
        createdBy =userId       
    ) 
   
    try:        
        db.add(new_consentRequest)  
        db.commit()      
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
        response_data.itemOwnerSeedorId=tmp_OwnerProfile.seedorId
        response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
        response_data.itemBeneficiarySeedor=profile.seedorId
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status
        response_data.itemType=new_consentRequest.itemType
        response_data.requestedBy=new_consentRequest.requestedBy
        response_data.requestedTo=new_consentRequest.requestedTo
        response_data.seqCounter=new_consentRequest.seqCounter
        response_data.consentValididtyFrequency=new_consentRequest.consentValididtyFrequency       
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Consent REVOKED Successfully"

    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Consent Grand Successfully")        

    return response_data


def rejectConsentOffer(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentRequestOut(
        idconsentrequest="",
        itemOwnerIdUser="", 
        itemOwnerSeedorId="", 
        itemBeneficiaryIdUser="",
        itemBeneficiarySeedor="",
        itemType="",
        itemId="",
        status="",
        consentValididtyFrequency="",
        requestedBy="",
        requestedTo="",
        seqCounter=0,
        isactiveConnection=False,
        consentSendStatus="User not Active",
        statuscode="ERROR",
        statusmessage="Invalid Consent Request Object"  
        )
    
    
    validateConsentItem(consentReq_in, db)
    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.itemBeneficiarySeedorId).first()
    tmp_Ownerprofile = db.query(Profile).filter(Profile.authIduser == userId).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Invalid Signatory Seedorid") 
    
    if not tmp_Ownerprofile:
        raise HTTPException(status_code=400, detail="Invalid Owner Seedorid")
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.itemOwnerIdUser ==userId ).filter(
        ConsentRequest.itemBeneficiaryIdUser ==  profile.authIduser).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()   
     
    tmp_seq = 1 if not tmp_seq or tmp_seq == 0 else tmp_seq + 1
    
    new_consentRequest=ConsentRequest(
        itemOwnerIdUser=profile.authIduser ,    
        itemBeneficiaryIdUser = userId,
        itemType=consentReq_in.itemType,  
        itemId=consentReq_in.itemId,  
        status="REJECT",
        consentValididtyFrequency=consentReq_in.consentValididtyFrequency,
        seqCounter=tmp_seq,
        requestedBy=userId,
        requestedTo=profile.authIduser,
        updatedBy = userId,
        createdBy =userId       
    ) 
   
    try:        
        db.add(new_consentRequest)  
        db.commit()      
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.itemOwnerIdUser= new_consentRequest.itemOwnerIdUser
        response_data.itemOwnerSeedorId=tmp_Ownerprofile.seedorId
        response_data.itemBeneficiaryIdUser=new_consentRequest.itemBeneficiaryIdUser
        response_data.itemBeneficiarySeedor=profile.seedorId
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status 
        response_data.requestedBy=new_consentRequest.requestedBy
        response_data.requestedTo=new_consentRequest.requestedTo
        response_data.seqCounter=new_consentRequest.seqCounter  
        response_data.itemType=new_consentRequest.itemType
        response_data.consentValididtyFrequency=new_consentRequest.consentValididtyFrequency       
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Consent REVOKED Successfully"

    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Consent Grand Successfully")        

    return response_data


def getconsentRequestHistoryItemType(payload: dict,consentReq_in: ConsentRequestGETIN,  request: Request,  db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    consent_listOut=ConsentRequestallOUT(
        listConsentRequest=[],
        statuscode="ERROR",
        statusmessage="No Consent Found" 
        )

    consent_list=db.query(ConsentRequest).filter(ConsentRequest.itemType == consentReq_in.itemType).filter(
        ConsentRequest.itemOwnerIdUser==userId).order_by(ConsentRequest.itemId,ConsentRequest.seqCounter.desc()).all()
    
    for tmpconsentRequ in consent_list: 
         tmp_OwnerProfile=db.query(Profile).filter(Profile.authIduser==tmpconsentRequ.itemOwnerIdUser).first()
         tmp_BeneficiaryProfile=db.query(Profile).filter(Profile.authIduser==tmpconsentRequ.itemBeneficiaryIdUser).first()
         tmpconsentRequestBaseModel=ConsentRequest(
            idconsentrequest=tmpconsentRequ.idconsentrequest,
            itemOwnerIdUser= tmp_OwnerProfile.seedorId,  
            itemBeneficiaryIdUser=tmp_BeneficiaryProfile.seedorId,
            itemType=tmpconsentRequ.itemType,
            itemId=tmpconsentRequ.itemId,
            status=tmpconsentRequ.status,
            consentValididtyFrequency=tmpconsentRequ.consentValididtyFrequency,
            requestedBy=tmpconsentRequ.requestedBy,
            requestedTo=tmpconsentRequ.requestedTo,
            createdBy=tmpconsentRequ.createdBy,
            updatedBy=tmpconsentRequ.updatedBy,
            createdDate=tmpconsentRequ.createdDate,
            updatedDate=tmpconsentRequ.updatedDate,
            seqCounter=tmpconsentRequ.seqCounter,
                  
         )
         consent_listOut.listConsentRequest.append(tmpconsentRequestBaseModel)          
   
    consent_listOut.statuscode="SUCCESS"
    consent_listOut.statusmessage="Consent Found" 

    response_data=consent_listOut

    return response_data

def getconsentRequestHistoryItemId(payload: dict,consentReq_in: ConsentRequestGETIN,  request: Request,  db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    tmp_consentReq_Out=ConsentRequestOut(
        idconsentrequest="",
        itemOwnerIdUser="", 
        itemOwnerSeedorId="",
        itemBeneficiaryIdUser="",
        itemBeneficiarySeedor="",
        itemType="",
        itemId="",
        status="",
        consentValididtyFrequency="",
        requestedBy="",
        requestedTo="",
        seqCounter=0,
        isactiveConnection=False,
        consentSendStatus="",
        statuscode="ERROR",
        statusmessage="No Consent Found" 
        )

    consentReq_Out=db.query(ConsentRequest).filter(ConsentRequest.itemId == consentReq_in.itemId).filter(
        ConsentRequest.itemOwnerIdUser==userId).first()
    if consentReq_Out:
         tmp_OwnerProfile=db.query(Profile).filter(Profile.authIduser==consentReq_Out.itemOwnerIdUser).first()
         tmp_BeneficiaryProfile=db.query(Profile).filter(Profile.authIduser==consentReq_Out.itemBeneficiaryIdUser).first()
         tmpconsentRequestBaseModel=ConsentRequestOut(
            idconsentrequest=consentReq_Out.idconsentrequest,
            itemOwnerIdUser= tmp_OwnerProfile.authIduser,  
            itemOwnerSeedorId=tmp_OwnerProfile.seedorId,
            itemBeneficiaryIdUser=tmp_BeneficiaryProfile.authIduser,
            itemBeneficiarySeedor=tmp_BeneficiaryProfile.seedorId,
            itemType=consentReq_Out.itemType,
            itemId=consentReq_Out.itemId,
            status=consentReq_Out.status,
            consentValididtyFrequency=consentReq_Out.consentValididtyFrequency,
            requestedBy=consentReq_Out.requestedBy,
            requestedTo=consentReq_Out.requestedTo,
            seqCounter=consentReq_Out.seqCounter,
            isactiveConnection=False,
            consentSendStatus="",
            statuscode="SUCCESS",
            statusmessage="Consent Found"          
         )
         tmp_consentReq_Out=tmpconsentRequestBaseModel   

    response_data=tmp_consentReq_Out
    return response_data


def getconsentRequestBeneficiaryHistoryItemType(payload: dict,consentReq_in: ConsentRequestGETIN,  request: Request,  db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    consent_listOut=ConsentRequestallOUT(
        listConsentRequest=[],
        statuscode="ERROR",
        statusmessage="No Consent Found" 
        )

    consent_list=db.query(ConsentRequest).filter(ConsentRequest.itemType == consentReq_in.itemType).filter(
        ConsentRequest.itemBeneficiaryIdUser==userId).order_by(ConsentRequest.itemId,ConsentRequest.seqCounter.desc()).all()
    
    for tmpconsentRequ in consent_list: 
         tmp_OwnerProfile=db.query(Profile).filter(Profile.authIduser==tmpconsentRequ.itemOwnerIdUser).first()
         tmp_BeneficiaryProfile=db.query(Profile).filter(Profile.authIduser==tmpconsentRequ.itemBeneficiaryIdUser).first()
         tmpconsentRequestBaseModel=ConsentRequest(
            idconsentrequest=tmpconsentRequ.idconsentrequest,
            itemOwnerIdUser= tmp_OwnerProfile.seedorId, 
            itemBeneficiaryIdUser=tmp_BeneficiaryProfile.seedorId,
            itemType=tmpconsentRequ.itemType,
            itemId=tmpconsentRequ.itemId,
            status=tmpconsentRequ.status,
            consentValididtyFrequency=tmpconsentRequ.consentValididtyFrequency,
            requestedBy=tmpconsentRequ.requestedBy,
            requestedTo=tmpconsentRequ.requestedTo,
            createdBy=tmpconsentRequ.createdBy,
            updatedBy=tmpconsentRequ.updatedBy,
            createdDate=tmpconsentRequ.createdDate,
            updatedDate=tmpconsentRequ.updatedDate,
            seqCounter=tmpconsentRequ.seqCounter,
                  
         )
         consent_listOut.listConsentRequest.append(tmpconsentRequestBaseModel)          
   
    consent_listOut.statuscode="SUCCESS"
    consent_listOut.statusmessage="Consent Found" 

    response_data=consent_listOut

    return response_data


def getconsentRequestBeneficiaryHistoryItemId(payload: dict,consentReq_in: ConsentRequestGETIN,  request: Request,  db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    tmp_consentReq_Out=ConsentRequestOut(
        idconsentrequest="",
        itemOwnerIdUser="", 
        itemOwnerSeedorId="",
        itemBeneficiaryIdUser="",
        itemBeneficiarySeedor="",
        itemType="",
        itemId="",
        status="",
        consentValididtyFrequency="",
        requestedBy="",
        requestedTo="",
        seqCounter=0,
        isactiveConnection=False,
        consentSendStatus="",
        statuscode="ERROR",
        statusmessage="No Consent Found" 
        )

    consentReq_Out=db.query(ConsentRequest).filter(ConsentRequest.itemId == consentReq_in.itemId).filter(
        ConsentRequest.itemBeneficiaryIdUser==userId).first()
    if consentReq_Out:
         tmp_OwnerProfile=db.query(Profile).filter(Profile.authIduser==consentReq_Out.itemOwnerIdUser).first()
         tmp_BeneficiaryProfile=db.query(Profile).filter(Profile.authIduser==consentReq_Out.itemBeneficiaryIdUser).first()
         tmpconsentRequestBaseModel=ConsentRequestOut(
            idconsentrequest=consentReq_Out.idconsentrequest,
            itemOwnerIdUser= tmp_OwnerProfile.authIduser,  
            itemOwnerSeedorId=tmp_OwnerProfile.seedorId,
            itemBeneficiaryIdUser=tmp_BeneficiaryProfile.authIduser,
            itemBeneficiarySeedor=tmp_BeneficiaryProfile.seedorId,
            itemType=consentReq_Out.itemType,
            itemId=consentReq_Out.itemId,
            status=consentReq_Out.status,
            consentValididtyFrequency=consentReq_Out.consentValididtyFrequency,
            requestedBy=consentReq_Out.requestedBy,
            requestedTo=consentReq_Out.requestedTo,
            seqCounter=consentReq_Out.seqCounter,
            isactiveConnection=False,
            consentSendStatus="",
            statuscode="SUCCESS",
            statusmessage="Consent Found"          
         )
         tmp_consentReq_Out=tmpconsentRequestBaseModel   

    response_data=tmp_consentReq_Out
    return response_data