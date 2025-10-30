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
from app.db.models import Base, User,Profile,Lov
from app.schemas.schemas import UserProfile, UserProfileOut,ValidateSeedorId,ValidateSeedorIdOut
from app.api.auth import hash_password, create_access_token, verify_password,verify_access_token,get_bearer_token,manual_basic_auth,verify_basic_auth
from app.core.rate_limit import check_rate_limit
from email_validator import validate_email, EmailNotValidError
from app.core.email_security import send_verification_email
from app.utils.emailauth_utils import create_email_token, verify_email_token
from app.api.user import registerUser,validateUserName,validateLogin
from app.api.master import getLov

def updateProfile(payload: dict,userProfile_in: UserProfile, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    profile = db.query(Profile).filter(Profile.idprofile == profileId).first()
    response_data=UserProfileOut(
        idprofile="",
        statuscode="ERROR",
        statusmessage="Invalid User Profile"  
    )
    if profile:
        try:
            if  userProfile_in.seedorId and userProfile_in.seedorId.strip() != "":
                if(not profile.isValidSeedorId):                
                    profile.seedorId=userProfile_in.seedorId
                    profile.isValidSeedorId=True
            if  userProfile_in.preferedName and userProfile_in.preferedName.strip() != "":
                profile.preferedName =userProfile_in.preferedName 
            if  userProfile_in.firstName and userProfile_in.firstName.strip() != "":
                profile.firstName=userProfile_in.firstName
            if  userProfile_in.middleName and userProfile_in.middleName.strip() != "":
                profile.middleName = userProfile_in.middleName
            if  userProfile_in.lastName and userProfile_in.lastName.strip() != "":
                profile.lastName = userProfile_in.lastName
            if  userProfile_in.phone and userProfile_in.phone.strip() != "":
                profile.phone = userProfile_in.phone
            if  userProfile_in.countryCode and userProfile_in.countryCode.strip() != "":
                profile.countryCode= userProfile_in.countryCode
            if  userProfile_in.countryName and userProfile_in.countryName.strip() != "":
                profile.countryName= userProfile_in.countryName    
            if  userProfile_in.profileType and userProfile_in.profileType.strip() != "":
                profile.profileType=userProfile_in.profileType

            profile.updatedBy =userId         
            db.commit()
            db.refresh(profile) 
            response_data.idprofile=profile.idprofile
            response_data.statuscode="SUCCESS"
            response_data.statusmessage="Profile Updated Successfully"
        except IntegrityError as e:            
            db.rollback()
            raise HTTPException(status_code=400, detail="Profile update failed")
        

    return response_data

def validateSeedorId(payload: dict,newSeedorId_in: ValidateSeedorId,request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    profile=None
    if newSeedorId_in :
        profile = db.query(Profile).filter(Profile.seedorId == newSeedorId_in.seedorId).first()

    response_data=ValidateSeedorIdOut(
        seedorIdAvaiable=False,
        statuscode="ERROR",
        statusmessage="SeedorID Already Taken"  
    )

    if not profile :
        response_data.seedorIdAvaiable=True
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="SeedorId Available"
           

    return response_data