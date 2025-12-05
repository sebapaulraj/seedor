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
from app.db.addressmodel import Base, Address
from app.schemas.schemas import AddressBase, AddressDeleteIN, AddressNewIN, AddressOut, AddressGetIN,AddressGetOUT,AddressUpdateIN
from app.api.auth import hash_password, create_access_token, verify_password,verify_access_token,get_bearer_token,manual_basic_auth,verify_basic_auth
from app.core.rate_limit import check_rate_limit
from email_validator import validate_email, EmailNotValidError
from app.core.email_security import send_verification_email
from app.utils.emailauth_utils import create_email_token, verify_email_token

def addAddress(payload: dict,address_in: AddressNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=AddressOut(
        idaddress="",
        addressId="",
        isActive=False,
        statuscode="ERROR",
        statusmessage="Invalid Address Profile"  
    )   
    
    tmp_count= db.query(func.count(Address.idaddress)).filter(Address.idUser == userId).scalar()
    if not tmp_count or tmp_count==0:
        tmp_count=1
    else:
        tmp_count=tmp_count+1

    profile=db.query(Profile).filter(Profile.idprofile == profileId).first()
    

    tmp_addressId=profile.seedorId
    tmp_addressCode="AD"

    new_Address=Address(
        idUser=userId,
        addressId=tmp_addressId+"/"+tmp_addressCode+"/"+str(tmp_count),
        isActive=True            
    )
    new_Address.label= address_in.label
    new_Address.primaryAddress= True
    new_Address.street=address_in.street
    new_Address.area=address_in.area
    new_Address.city=address_in.city
    new_Address.stateorProvince=address_in.stateorProvince 
    new_Address.postalCode=address_in.postalCode
    new_Address.country=address_in.country
    new_Address.createdBy = userId
    new_Address.updatedBy = userId 
    try:
        # Deactivate old primary addresses
        db.query(Address).filter_by(idUser=new_Address.idUser, primaryAddress=1).update({"primaryAddress": 0})
        db.add(new_Address)
        db.commit()
        db.refresh(new_Address) 
        response_data.idaddress=new_Address.idaddress
        response_data.addressId=new_Address.addressId
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Address Added Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Address Apdate Failed")        

    return response_data

def updateAddress(payload: dict,address_in: AddressUpdateIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=AddressOut(
        idaddress="",
        addressId="",
        isActive=False,
        statuscode="ERROR",
        statusmessage="Invalid Address Update"  
        )
    
    new_Address=None
    if address_in.idaddress :
        if address_in.primaryAddress==True:
            db.query(Address).filter_by(idUser=new_Address.idUser, primaryAddress=1).update({"primaryAddress": 0})
        
        new_Address = db.query(Address).filter(Address.idaddress == address_in.idaddress).first()
        #new_Address.isActive=address_in.isActive
        new_Address.label= address_in.label
        new_Address.primaryAddress= address_in.primaryAddress
       # new_Address.street=address_in.street
       # new_Address.area=address_in.area
       # new_Address.city=address_in.city
       # new_Address.stateorProvince=address_in.stateorProvince 
       # new_Address.postalCode=address_in.postalCode
      #  new_Address.country=address_in.country
       # new_Address.createdBy = userId
        new_Address.updatedBy = userId 
        new_Address.updatedDate=func.now()
    try:
        db.commit()
        db.refresh(new_Address) 
        response_data.idaddress=new_Address.idaddress
        response_data.addressId=new_Address.addressId
        response_data.isActive=new_Address.isActive
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Address Updated Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Address Update Failed")        

    return response_data

def getAddressesId(payload: dict,address_in: AddressGetIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    address_listOut=AddressGetOUT(
        listAddress=[],
        statuscode="ERROR",
        statusmessage="No Address Found" 
        )
    
    address = db.query(Address).filter(Address.addressId == address_in.addressId).first()
    if not address :
        response_data=address_listOut
        return response_data
     
    tmp_AddressBase=AddressBase(
            idaddress = address.idaddress, 
            addressId=address.addressId,
            isActive= address.isActive,
            label= address.label,
            primaryAddress= address.primaryAddress,
            street=address.street,
            area=address.area,
            city=address.city,
            postalCode=address.postalCode,
            country=address.country
        )  
    address_listOut.listAddress.append(tmp_AddressBase)
    address_listOut.statuscode="SUCCESS"
    address_listOut.statusmessage="Address Found" 
    
    response_data=address_listOut

    return response_data


def getAddressesAll(payload: dict, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    address_listOut=AddressGetOUT(
        listAddress=[],
        statuscode="ERROR",
        statusmessage="No Address Found" 
        )
    
    address_list=db.query(Address).filter(Address.idUser == userId).all()        
    for tmpAddress in address_list:
        tmp_AddressBase=AddressBase(
            idaddress = tmpAddress.idaddress, 
            addressId=tmpAddress.addressId,
            isActive= tmpAddress.isActive,
            label= tmpAddress.label,
            primaryAddress= tmpAddress.primaryAddress,
            street=tmpAddress.street,
            area=tmpAddress.area,
            city=tmpAddress.city,
            postalCode=tmpAddress.postalCode,
            country=tmpAddress.country
        )            
        address_listOut.listAddress.append(tmp_AddressBase)

    address_listOut.statuscode="SUCCESS"
    address_listOut.statusmessage="Address Found" 

    response_data=address_listOut

    return response_data

def deleteAddress(payload: dict,address_in: AddressDeleteIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=AddressOut(
        idaddress="",
        addressId="",
        isActive=False,
        statuscode="ERROR",
        statusmessage="Invalid Address Update"  
        )
    
    new_Address=None
    if address_in.idaddress :
        new_Address = db.query(Address).filter(Address.idaddress == address_in.idaddress).first()
        new_Address.isActive=False
       # new_Address.label= address_in.label
       # new_Address.primaryAddress= address_in.primaryAddress
       # new_Address.street=address_in.street
       # new_Address.area=address_in.area
       # new_Address.city=address_in.city
       # new_Address.stateorProvince=address_in.stateorProvince 
       # new_Address.postalCode=address_in.postalCode
       # new_Address.country=address_in.country
       # new_Address.createdBy = userId
        new_Address.updatedBy = userId 
    try:
        db.commit()
        db.refresh(new_Address) 
        response_data.idaddress=new_Address.idaddress
        response_data.addressId=new_Address.addressId
        response_data.isActive=new_Address.isActive
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Address Deleted Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Address Delete Failed")        

    return response_data