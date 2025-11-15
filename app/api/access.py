import os
import json
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.db.db import get_db, engine
from app.db.accessmodel import Access
from app.db.models import Base
from app.schemas.schemas import AccessBase, AccessGetIdIN, AccessGetIdTypeIN, AccessNewIN, AccessOut, AccessGetIN,AccessGetOUT


def grandAccess(payload: dict,access_in: AccessNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=AccessOut(
        idaccess="",
        accessStatus="",
        seqCounter=0,
        statuscode="ERROR",
        statusmessage="Invalid Access Object"  
    )    

    tmp_count= db.query(func.count(Access.idaccess)).filter(Access.idUser == userId).filter(Access.accessTypeId == access_in.accessTypeId).scalar()
    if tmp_count==0:
        tmp_count=1
    else:
        tmp_count=tmp_count+1
    
    new_Access=Access(
        idUser=userId,
        accessTypeId=access_in.accessTypeId,
        accessTypeValue=access_in.accessTypeValue,  
        accessStatus="GRAND",
        seqCounter=tmp_count,
        createdBy = userId,
        updatedBy = userId    
        )
       
    try:
        db.add(new_Access)
        db.commit()
        db.refresh(new_Access) 
        response_data.idaccess=new_Access.idaccess
        response_data.accessStatus=new_Access.accessStatus
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Access Added Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Access update failed")        

    return response_data

def revokeAccess(payload: dict,access_in: AccessNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=AccessOut(
        idaccess="",
        accessStatus="",
        seqCounter=0,
        statuscode="ERROR",
        statusmessage="Invalid Access Object"  
    )    

    tmp_count= db.query(func.count(Access.idaccess)).filter(Access.idUser == userId).filter(Access.accessTypeId == access_in.accessTypeId).scalar()
    if not tmp_count or tmp_count==0:
        raise HTTPException(status_code=400, detail="No Access Grand to Revoke")          
    else:
        tmp_count=tmp_count+1
    
    new_Access=Access(
        idUser=userId,
        accessTypeId=access_in.accessTypeId,
        accessTypeValue=access_in.accessTypeValue,  
        accessStatus="REVOKE",
        seqCounter=tmp_count,
        createdBy = userId,
        updatedBy = userId    
        )
       
    try:
        db.add(new_Access)
        db.commit()
        db.refresh(new_Access) 
        response_data.idaccess=new_Access.idaccess
        response_data.accessStatus=new_Access.accessStatus
        response_data.seqCounter=new_Access.seqCounter
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Access Added Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Access update failed")        

    return response_data


def getAccessById(payload: dict,access_in: AccessGetIdIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    access_listOut=AccessGetOUT(
        listAccess=[],
        statuscode="ERROR",
        statusmessage="No Access Detail" 
        )
    
    if access_in.idaccess :
        tmp_seq= db.query(func.max(Access.seqCounter)).filter(Access.idUser == userId).filter(Access.idaccess == access_in.idaccess).scalar()    
        if not tmp_seq:            
            response_data=access_listOut
            return response_data
        
        tmp_access = db.query(Access).filter(Access.idaccess == access_in.idaccess).filter(Access.seqCounter==tmp_seq).first()
        tmp_AccessBase=AccessBase(
            idaccess =tmp_access.idaccess,
            idUser=tmp_access.idUser,  
            accessTypeId=tmp_access.accessTypeId,
            accessTypeValue=tmp_access.accessTypeValue,
            accessGrantedOn=str(tmp_access.accessGrantedOn),
            accessStatus=tmp_access.accessStatus,
            seqCounter=tmp_access.seqCounter
        )
        access_listOut.listAccess.append(tmp_AccessBase)
        access_listOut.statuscode="SUCCESS"
        access_listOut.statusmessage="Access Found" 
    
    response_data=access_listOut

    return response_data

def getTypeIdAccess(payload: dict,access_in: AccessGetIdTypeIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    access_listOut=AccessGetOUT(
        idaccess="",
        listAccess=[],
        statuscode="ERROR",
        statusmessage="No Access Detail" 
        )
    
    if access_in.accessTypeId :
        tmp_seq= db.query(func.max(Access.seqCounter)).filter(Access.idUser == userId).filter(Access.accessTypeId == access_in.accessTypeId).scalar()    
        if not tmp_seq:            
            response_data=access_listOut
            return response_data
        
        tmp_access = db.query(Access).filter(Access.idUser == userId).filter(Access.accessTypeId == access_in.accessTypeId).filter(Access.seqCounter==tmp_seq).first()
        tmp_AccessBase=AccessBase(
            idaccess =tmp_access.idaccess,
            idUser=tmp_access.idUser,  
            accessTypeId=tmp_access.accessTypeId,
            accessTypeValue=tmp_access.accessTypeValue,
            accessGrantedOn=str(tmp_access.accessGrantedOn),
            accessStatus=tmp_access.accessStatus,
            seqCounter=tmp_access.seqCounter
        )
        access_listOut.listAccess.append(tmp_AccessBase)       
        access_listOut.statuscode="SUCCESS"
        access_listOut.statusmessage="Access Found" 
    
    response_data=access_listOut

    return response_data


def getHistoryAccess(payload: dict,access_in: AccessGetIdTypeIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    access_listOut=AccessGetOUT(
        idaccess="",
        listAccess=[],
        seqCounter=0,
        statuscode="ERROR",
        statusmessage="No Access Detail" 
        )
    
    if access_in.accessTypeId :
       # tmp_seq= db.query(func.max(Access.seqCounter)).filter(Access.idUser == userId).filter(Access.accessTypeId == access_in.accessTypeId).scalar()    
       # print(f"{access_in.accessTypeId} and {userId}")
        tmp_accesslist = db.query(Access).filter(Access.idUser == userId).filter(Access.accessTypeId == access_in.accessTypeId).order_by(desc(Access.createdDate)).all()
        for item_Access in tmp_accesslist:
            tmp_AccessBase=AccessBase(
                idaccess =item_Access.idaccess,
                idUser=item_Access.idUser,  
                accessTypeId=item_Access.accessTypeId,
                accessTypeValue=item_Access.accessTypeValue,
                accessGrantedOn=str(item_Access.accessGrantedOn),
                accessStatus=item_Access.accessStatus,
                seqCounter=item_Access.seqCounter
            )
            access_listOut.listAccess.append(tmp_AccessBase)       
        access_listOut.statuscode="SUCCESS"
        access_listOut.statusmessage="Access Found" 
    
    response_data=access_listOut

    return response_data

def getHistoryAccessAll(payload: dict,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    access_listOut=AccessGetOUT(
        listAccess=[],
        statuscode="ERROR",
        statusmessage="No Access Detail" 
        )
    
   # if access_in.accessTypeId :
       # tmp_seq= db.query(func.max(Access.seqCounter)).filter(Access.idUser == userId).filter(Access.accessTypeId == access_in.accessTypeId).scalar()    
       # print(f"{access_in.accessTypeId} and {userId}")
    tmp_accesslist = db.query(Access).filter(Access.idUser == userId).order_by(desc(Access.createdDate)).all()
    for item_Access in tmp_accesslist:
        tmp_AccessBase=AccessBase(
            idaccess =item_Access.idaccess,
            idUser=item_Access.idUser,  
            accessTypeId=item_Access.accessTypeId,
            accessTypeValue=item_Access.accessTypeValue,
            accessGrantedOn=str(item_Access.accessGrantedOn),
            accessStatus=item_Access.accessStatus,
            seqCounter=item_Access.seqCounter
        )
        access_listOut.listAccess.append(tmp_AccessBase)       
    access_listOut.statuscode="SUCCESS"
    access_listOut.statusmessage="Access List Found " 
    
    response_data=access_listOut

    return response_data

'''
def updateAccess(payload: dict,access_in: AccessUpdateIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    email=payload["email"]    
    
    response_data=AccessOut(
        idaccess=None,
        accessStatus=None,
        statuscode="ERROR",
        statusmessage="Invalid Access Object"  
        )
    
    new_Access=None
    if access_in.idaccess :
        new_Access = db.query(Access).filter(Access.idaccess == access_in.idaccess).first()
   
    new_Access.accessStatus=access_in.accessStatus,
    new_Access.createdBy = userId,
    new_Access.updatedBy = userId    
    try:
        db.commit()
        db.refresh(new_Access) 
        response_data.idaccess=new_Access.idaccess
        response_data.accessStatus=new_Access.accessStatus
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Access Updated Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Access Update Failed")        

    return response_data
'''