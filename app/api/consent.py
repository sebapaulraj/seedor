import os
import json
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.db.db import get_db, engine
from app.db.models import Base, Consent
from app.schemas.schemas import ConsentNewIN, ConsentOut, ConsentGetIN,ConsentGetOUT,ConsentUpdateIN


def addConsent(payload: dict,consent_in: ConsentNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentOut(
        idconsent=None,
        isActive=None,
        statuscode="ERROR",
        statusmessage="Invalid consent Object"  
    )    
    
    new_consent=Consent(
        offerorIdUser=userId,
        signatoryIdUser= consent_in.signatoryIdUser,
        offerorSeedorId= consent_in.offerorSeedorId,
        signatorySeedorId= consent_in.signatorySeedorId,
        itemType= consent_in.itemType,
        itemId=consent_in.itemId, 
        status=consent_in.status,
        isActive=True,
        createdBy = userId,
        updatedBy = userId    
    )
       
    try:
        db.commit()
        db.refresh(new_consent) 
        response_data.idconsent=new_consent.idconsent
        response_data.isActive=new_consent.isActive
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="consent Added Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Address update failed")        

    return response_data

def updateConsent(payload: dict,consent_in: ConsentUpdateIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ConsentOut(
        idconsent=None,
        isActive=None,
        statuscode="ERROR",
        statusmessage="Invalid consent Object"  
        )
    
    new_consent=None
    if consent_in.idconsent :
        new_consent = db.query(Consent).filter(Consent.idconsent == consent_in.idconsent).first()
   
    new_consent.isActive=consent_in.isActive,
    new_consent.createdBy = userId,
    new_consent.updatedBy = userId    
    try:
        db.commit()
        db.refresh(new_consent) 
        response_data.idconsent=new_consent.idconsent
        response_data.consentStatus=new_consent.consentStatus
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="consent Updated Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="consent Update Failed")        

    return response_data

def getconsent(payload: dict,consent_in: ConsentGetIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    consent_listOut=ConsentGetOUT(
        idUser=None,
        listAddress=None,
        statuscode="ERROR",
        statusmessage="No Address Found" 
        )

    if consent_in.idaddress :
        consent = db.query(consent).filter(consent.idaddress == consent_in.idaddress).first()
        consent_listOut.idUser=userId
        consent_listOut.listconsent.append(consent)
        statuscode="SUCCESS"
        statusmessage="Address Found" 
    else:
        consent_list=db.query(consent).filter(consent.idUser == userId).all()
        consent_listOut.idUser=userId
        for tmpconsent in consent_list:            
            consent_listOut.listconsent.append(tmpconsent)
        statuscode="SUCCESS"
        statusmessage="Address Found" 

    response_data=consent_listOut

    return response_data
