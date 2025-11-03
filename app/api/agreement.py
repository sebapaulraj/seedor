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
from app.db.db import get_db, engine
from app.db.usermodel import Profile
from app.db.agreementmodel import Agreement
from app.db.models import Base
from app.schemas.schemas import AgreementBase, AgreementDeleteIN, AgreementNewIN, AgreementOut, AgreementGetIN,AgreementGetOUT,AgreementUpdateIN


def addAgreement(payload: dict,agreement_in: AgreementNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=AgreementOut(
        idagreement="",
        isActive=False,
        statuscode="ERROR",
        statusmessage="Invalid Agreement Object"  
    )   

    tmp_count= db.query(func.count(Agreement.idUser)).filter(Agreement.idUser == userId).scalar()
    if not tmp_count or tmp_count==0:
        tmp_count=1

    profile=db.query(Profile).filter(Profile.idprofile == profileId).first() 

    tmp_seedorId=profile.seedorId
    tmp_Code="AG"
    
    new_Agreement=Agreement(        
        agreementId=tmp_seedorId+"/"+tmp_Code+"/"+str(tmp_count),
        idUser=userId,
        label= agreement_in.label,
        title= agreement_in.title,
        summary= agreement_in.summary,
        content= agreement_in.content,
        details=agreement_in.details, 
        isActive=True,
        createdBy = userId,
        updatedBy = userId    
    )
       
    try:
        db.add(new_Agreement)
        db.commit()
        db.refresh(new_Agreement) 
        response_data.idagreement=new_Agreement.idagreement
        response_data.isActive=new_Agreement.isActive
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Agreement Added Successfully"
    except IntegrityError as e:   
        print(e.detail)         
        db.rollback()
        raise HTTPException(status_code=400, detail="Agreement update failed")        

    return response_data

def updateAgreement(payload: dict,agreement_in: AgreementUpdateIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=AgreementOut(
        idagreement="",
        isActive=False,
        statuscode="ERROR",
        statusmessage="Invalid Agreement Object"  
        )
    
    new_Agreement=None
    if agreement_in.idagreement :
        new_Agreement = db.query(Agreement).filter(Agreement.idagreement == agreement_in.idagreement).first()

        new_Agreement.label=agreement_in.label,
        new_Agreement.title=agreement_in.title,
        new_Agreement.summary=agreement_in.summary,
        new_Agreement.content=agreement_in.content,  
        new_Agreement.details=agreement_in.details,        
        new_Agreement.createdBy = userId,
        new_Agreement.updatedBy = userId    
    try:
        db.commit()
        db.refresh(new_Agreement) 
        response_data.idagreement=new_Agreement.idagreement
        response_data.isActive=new_Agreement.isActive
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Agreement Updated Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Agreement Update Failed")        

    return response_data

def getAgreementId(payload: dict,agreement_in: AgreementGetIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    agreement_listOut=AgreementGetOUT(
        listAgreement=[],
        statuscode="ERROR",
        statusmessage="No Agreement Found" 
        )
      
    tmp_agreement = db.query(Agreement).filter(Agreement.agreementId == agreement_in.agreementId).first()
    
    agreement_listOut.listAgreement.append(tmp_agreement)
    agreement_listOut.statuscode="SUCCESS"
    agreement_listOut.statusmessage="Agreement Found"                 
    
    response_data=agreement_listOut

    return response_data


def getAgreementAll(payload: dict, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    agreement_listOut=AgreementGetOUT(
        listAgreement=[],
        statuscode="ERROR",
        statusmessage="No Agreement Found" 
        )
      
    agreement_list=db.query(Agreement).filter(Agreement.idUser == userId).all() 
    for tmpAgreement in agreement_list:
        tmp_agreementBase=AgreementBase(
        idagreement=tmpAgreement.idagreement,
        agreementId= tmpAgreement.agreementId,
        label= tmpAgreement.label,
        title= tmpAgreement.title,
        summary= tmpAgreement.summary,
        content= tmpAgreement.content,
        details=tmpAgreement.details,
        isActive=True            
        )                
        agreement_listOut.listAgreement.append(tmp_agreementBase)

    agreement_listOut.statuscode="SUCCESS"
    agreement_listOut.statusmessage="Agreement Found" 

    response_data=agreement_listOut

    return response_data


def deleteAgreement(payload: dict,agreement_in: AgreementDeleteIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=AgreementOut(
        idagreement="",
        isActive=False,   
        statuscode="ERROR",
        statusmessage="Invalid Agreement Update"  
        )
    
    new_Agreement=None
    if agreement_in.idagreement :
        new_Agreement = db.query(Agreement).filter(Agreement.idagreement == agreement_in.idagreement).first()
        new_Agreement.isActive=False
       # new_Address.label= address_in.label
       # new_Address.primaryAddress= address_in.primaryAddress
       # new_Address.street=address_in.street
       # new_Address.area=address_in.area
       # new_Address.city=address_in.city
       # new_Address.stateorProvince=address_in.stateorProvince 
       # new_Address.postalCode=address_in.postalCode
      #  new_Address.country=address_in.country
       # new_Address.createdBy = userId
        new_Agreement.updatedBy = userId 
    try:
        db.commit()
        db.refresh(new_Agreement) 
        response_data.idagreement=new_Agreement.idagreement
        response_data.isActive=new_Agreement.isActive
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Agreement Deleted Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Agreement Delete Failed")        

    return response_data