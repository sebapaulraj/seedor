import os
import json
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.db.consentmodel import ConsentRequest,Consent
from app.db.db import get_db, engine
from app.db.addressmodel import Address
from app.db.usermodel import Profile
from app.db.models import Agreement, Base,  Shipment
from app.schemas.consentschema import ConsentModel, ConsentRequestNewIN, ConsentGetIN,ConsentGetOUT, ConsentRequestOut


def createConsentRequest(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentRequestOut(
        idconsentrequest="",
        offerorIdUser="",  
        signatoryIdUser="",
        itemType="",
        itemId="",
        status="",
        isActive=False,
        isactiveConnection=False,
        consentSendStatus="User Not Online",
        updatedDate="",
        statuscode="ERROR",
        statusmessage="Invalid consent Object"  
    )  

    validateConsentItem(consentReq_in, db)

    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.offerorSeedorId).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Invalid Signatory Seedorid") 
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.signatoryIdUser == userId).filter(
        ConsentRequest.offerorIdUser == profile.authIduser).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()  
      
    if not tmp_seq or  tmp_seq==0:
        tmp_seq=1
    else:
        tmp_seq=tmp_seq+1
    
    new_consentRequest=ConsentRequest(
        offerorIdUser=profile.authIduser ,    
        signatoryIdUser = userId,
        itemType=consentReq_in.itemType,
        itemId=consentReq_in.itemId,  
        status="REQUEST",
        seqCounter=tmp_seq,
        createdBy =userId,
        updatedBy = userId        
    )  
        
    try:
        db.add(new_consentRequest)
        db.commit()
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.offerorIdUser= new_consentRequest.offerorIdUser
        response_data.signatoryIdUser=new_consentRequest.signatoryIdUser
        response_data.itemType=new_consentRequest.itemType
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status
        response_data.updatedDate=new_consentRequest.updatedDate        
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Consent Request Raised Successfully"
    
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Consent Request failed")        

    return response_data

def createConsentOffer(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentRequestOut(
        idconsentrequest="",
        offerorIdUser="",  
        signatoryIdUser="",
        itemType="",
        itemId="",
        status="",
        isActive=False,
        isactiveConnection=False,
        consentSendStatus="User Not Online",
        updatedDate="",
        statuscode="ERROR",
        statusmessage="Invalid consent Object"  
    )  

    validateConsentItem(consentReq_in, db)

    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.signatorySeedorId).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Invalid Signatory Seedorid") 
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.signatoryIdUser == profile.authIduser ).filter(
        ConsentRequest.offerorIdUser == userId).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()  
      
    if not tmp_seq or  tmp_seq==0:
        tmp_seq=1
    else:
        tmp_seq=tmp_seq+1
    
    new_consentRequest=ConsentRequest(
        offerorIdUser=userId ,    
        signatoryIdUser = profile.authIduser,
        itemType=consentReq_in.itemType,
        itemId=consentReq_in.itemId,  
        status="REQUEST",
        seqCounter=tmp_seq,
        createdBy =userId,
        updatedBy = userId        
    )  
        
    try:
        db.add(new_consentRequest)
        db.commit()
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.offerorIdUser= new_consentRequest.offerorIdUser
        response_data.signatoryIdUser=new_consentRequest.signatoryIdUser
        response_data.itemType=new_consentRequest.itemType
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status
        response_data.updatedDate=new_consentRequest.updatedDate        
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Consent Request Raised Successfully"
    
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Consent Request failed")        

    return response_data

def acceptConsentRequest(payload: dict,consentReq_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentRequestOut(
        idconsentrequest="",
        offerorIdUser="",  
        signatoryIdUser="",
        itemType="",
        itemId="",
        status="",
        isactiveConnection=False,
        consentSendStatus="User not Active",
        updatedDate="",
        statuscode="ERROR",
        statusmessage="Invalid consent Object"  
        )
    
         
    validateConsentItem(consentReq_in, db)
    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.signatorySeedorId).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Invalid Signatory Seedorid") 
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.offerorIdUser == userId ).filter(
        ConsentRequest.signatoryIdUser == profile.authIduser ).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()    
    if not tmp_seq or tmp_seq==0:
        tmp_seq=1
    else:
        tmp_seq=tmp_seq+1
    
    new_consentRequest=ConsentRequest(
        offerorIdUser=profile.authIduser ,    
        signatoryIdUser = userId,
        itemType=consentReq_in.itemType,  
        itemId=consentReq_in.itemId,  
        status="ACCEPT",
        seqCounter=tmp_seq,
        createdBy =userId,
        updatedBy = userId        
    ) 
              
    try:        
        db.add(new_consentRequest)
       # db.add(new_consent)
        db.commit()
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.offerorIdUser= new_consentRequest.offerorIdUser
        response_data.signatoryIdUser=new_consentRequest.signatoryIdUser
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status
        response_data.updatedDate=new_consentRequest.updatedDate        
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
        offerorIdUser="",  
        signatoryIdUser="",
        itemType="",
        itemId="",
        status="",
        isactiveConnection=False,
        consentSendStatus="User not Active",
        updatedDate="",
        statuscode="ERROR",
        statusmessage="Invalid consent Object"  
        )
    
         
    validateConsentItem(consentReq_in, db)
    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.offerorSeedorId).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Invalid Signatory Seedorid") 
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.offerorIdUser == userId ).filter(
        ConsentRequest.signatoryIdUser == profile.authIduser ).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()    
    if not tmp_seq or tmp_seq==0:
        tmp_seq=1
    else:
        tmp_seq=tmp_seq+1
    
    new_consentRequest=ConsentRequest(
        offerorIdUser= userId,    
        signatoryIdUser = profile.authIduser ,
        itemType=consentReq_in.itemType,  
        itemId=consentReq_in.itemId,  
        status="ACCEPT",
        seqCounter=tmp_seq,
        createdBy =userId,
        updatedBy = userId        
    ) 
              
    try:        
        db.add(new_consentRequest)
       # db.add(new_consent)
        db.commit()
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.offerorIdUser= new_consentRequest.offerorIdUser
        response_data.signatoryIdUser=new_consentRequest.signatoryIdUser
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status
        response_data.updatedDate=new_consentRequest.updatedDate        
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
        offerorIdUser="",  
        signatoryIdUser="",
        itemType="",
        itemId="",
        status="",
        isactiveConnection=False,
        consentSendStatus="User not Active",
        updatedDate="",
        statuscode="ERROR",
        statusmessage="Invalid consent Object"  
        )
    
    
    validateConsentItem(consentReq_in, db)
    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.signatorySeedorId).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Invalid Signatory Seedorid") 
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.offerorIdUser == userId).filter(
        ConsentRequest.signatoryIdUser == profile.authIduser).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()    
    if tmp_seq==0:
        tmp_seq=1
    else:
        tmp_seq=tmp_seq+1
    
    new_consentRequest=ConsentRequest(
        offerorIdUser=userId,    
        signatoryIdUser = profile.authIduser,
        itemType=consentReq_in.itemType,  
        itemId=consentReq_in.itemId,  
        status="REJECT",
        seqCounter=tmp_seq,
        updatedBy = userId,
        createdBy =userId       
    ) 
   
    try:        
        db.add(new_consentRequest)  
        db.commit()      
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.offerorIdUser= new_consentRequest.offerorIdUser
        response_data.signatoryIdUser=new_consentRequest.signatoryIdUser
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status
        response_data.updatedDate=new_consentRequest.updatedDate        
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
        offerorIdUser="",  
        signatoryIdUser="",
        itemType="",
        itemId="",
        status="",
        isactiveConnection=False,
        consentSendStatus="User not Active",
        updatedDate="",
        statuscode="ERROR",
        statusmessage="Invalid consent Object"  
        )
    
    
    validateConsentItem(consentReq_in, db)
    profile = db.query(Profile).filter(Profile.seedorId == consentReq_in.offerorSeedorId).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Invalid Signatory Seedorid") 
    
    tmp_seq= db.query(func.max(ConsentRequest.seqCounter)).filter(
        ConsentRequest.offerorIdUser == profile.authIduser ).filter(
        ConsentRequest.signatoryIdUser == userId).filter(
        ConsentRequest.itemId==consentReq_in.itemId).scalar()    
    if tmp_seq==0:
        tmp_seq=1
    else:
        tmp_seq=tmp_seq+1
    
    new_consentRequest=ConsentRequest(
        offerorIdUser=profile.authIduser ,    
        signatoryIdUser = userId,
        itemType=consentReq_in.itemType,  
        itemId=consentReq_in.itemId,  
        status="REJECT",
        seqCounter=tmp_seq,
        updatedBy = userId,
        createdBy =userId       
    ) 
   
    try:        
        db.add(new_consentRequest)  
        db.commit()      
        db.refresh(new_consentRequest) 
        response_data.idconsentrequest=new_consentRequest.idconsentrequest
        response_data.offerorIdUser= new_consentRequest.offerorIdUser
        response_data.signatoryIdUser=new_consentRequest.signatoryIdUser
        response_data.itemId=new_consentRequest.itemId
        response_data.status=new_consentRequest.status
        response_data.updatedDate=new_consentRequest.updatedDate        
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Consent REVOKED Successfully"

    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Consent Grand Successfully")        

    return response_data


def getConsentOfferd(payload: dict,consent_in: ConsentGetIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    consent_listOut=ConsentGetOUT(
        idconsent="",
        listConsent=[],
        statuscode="ERROR",
        statusmessage="No Address Found" 
        )

    if consent_in.idconsent :
        tmp_consent = db.query(Consent).filter(Consent.idconsent == consent_in.idconsent).first()
        consent_listOut.listConsent.append(tmp_consent)
        consent_listOut.statuscode="SUCCESS"
        consent_listOut.statusmessage="Address Found" 
    else:
        consent_list=db.query(Consent).filter(Consent.offerorIdUser == userId).all()
        for tmpconsent in consent_list: 
            tmpconsentBaseModel=ConsentModel(
                offerorIdUser= tmpconsent.offerorIdUser,
                signatoryIdUser=tmpconsent.signatoryIdUser,
                offerorSeedorId=tmpconsent.offerorSeedorId, 
                signatorySeedorId=tmpconsent.signatorySeedorId,
                itemType=tmpconsent.itemType,
                itemId=tmpconsent.itemId,
                status=tmpconsent.status,
                grantedOn=tmpconsent.grantedOn
            )           
            consent_listOut.listConsent.append(tmpconsentBaseModel)
        consent_listOut.statuscode="SUCCESS"
        consent_listOut.statusmessage="Address Found" 

    response_data=consent_listOut

    return response_data

def getConsentSigned(payload: dict,consent_in: ConsentGetIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    consent_listOut=ConsentGetOUT(
        idconsent="",
        listConsent=[],
        statuscode="ERROR",
        statusmessage="No Address Found" 
        )

    if consent_in.idaddress :
        tmp_consent = db.query(Consent).filter(Consent.idconsent == consent_in.idconsent).first()
        consent_listOut.listConsent.append(tmp_consent)
        consent_listOut.statuscode="SUCCESS"
        consent_listOut.statusmessage="Address Found" 
    else:
        consent_list=db.query(Consent).filter(Consent.signatoryIdUser == userId).all()
        for tmpconsent in consent_list: 
            tmpconsentBaseModel=ConsentModel(
                offerorIdUser= tmpconsent.offerorIdUser,
                signatoryIdUser=tmpconsent.signatoryIdUser,
                offerorSeedorId=tmpconsent.offerorSeedorId, 
                signatorySeedorId=tmpconsent.signatorySeedorId,
                itemType=tmpconsent.itemType,
                itemId=tmpconsent.itemId,
                status=tmpconsent.status,
                grantedOn=tmpconsent.grantedOn
            )           
            consent_listOut.listConsent.append(tmpconsentBaseModel)
        consent_listOut.statuscode="SUCCESS"
        consent_listOut.statusmessage="Address Found" 

    response_data=consent_listOut

    return response_data


def validateConsentItem(consentReq_in: ConsentRequestNewIN, db: Session = Depends(get_db)):
    item=None
    if consentReq_in.itemType=="ADDRESS":
        item = db.query(Address).filter(Address.idaddress == consentReq_in.itemId).first()

    if consentReq_in.itemType=="AGREEMENT":
        item = db.query(Agreement).filter(Agreement.idagreement == consentReq_in.itemId).first()

    if consentReq_in.itemType=="SHIPMENT":
        item = db.query(Shipment).filter(Shipment.idshipment == consentReq_in.itemId).first()
    
    if not item:
        raise HTTPException(status_code=400, detail="Invalid Item")     

