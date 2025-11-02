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
from app.db.usermodel import User,Profile
from app.db.models import Base 
from app.schemas.schemas import UserCreate, UserOut,LoginUser,LoginOut,UserName,UserNameOut
from app.api.auth import hash_password, verify_password


def registerUser(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    existing = db.query(User).filter(User.email == user_in.email).first()    
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = hash_password(user_in.password)

    new_user = User(
        email=user_in.email,
        password=hashed_password,
        name=user_in.name
    )

    try:
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user) 
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

    # Return user (without token in body); token could be returned or sent via secure cookie/HTTP-only cookie
    status_code = "SUCCESS"  # Success code
    status_message = "User created successfully"   
    # Create response data with status and message
    response_data = UserOut(
        iduser=new_user.iduser,
        is_active=new_user.is_active,
        statuscode=status_code,  # Include status
        statusmessage=status_message  # Include message
    )
    return response_data

def validateUserName(userName_in: UserName, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    existingUser = db.query(User).filter(User.email == userName_in.email).first()    
    if not existingUser:
        raise HTTPException(status_code=400, detail="User Not Found")
       
    response_data = UserNameOut(
        email = "",
        is_active=False,
        statuscode="ERROR",
        statusmessage="Invalid User"        
        )
    token = ""
    # Return user (without token in body); token could be returned or sent via secure cookie/HTTP-only cookie
    if existingUser:
        response_data.email=existingUser.email
        response_data.is_active=existingUser.is_active
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Valid User"

    return response_data


def validateLogin(login_in: LoginUser, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    existingUser = db.query(User).filter(User.email == login_in.email).first()    
    if not existingUser:
        raise HTTPException(status_code=400, detail="User Not Found")

    # Hash password
    hashed_password = existingUser.password

    verifyResult=verify_password(login_in.password, hashed_password)
    # Create a token (optional — you might want email verification first)
    
    response_data = LoginOut(
        idprofile = "",
        authIduser="",
        seedorId = "",
        isValidSeedorId=False,
        preferedName = "",
        firstName = "",
        middleName = "",
        lastName = "",
        email = "",
        phone = "",
        isPhoneVerified= False,
        profileType="",
        countryCode="",
        countryName="",
        statuscode="ERROR",
        statusmessage="Invalid User"        
        )
    token = ""
    # Return user (without token in body); token could be returned or sent via secure cookie/HTTP-only cookie
    if verifyResult:
        userProfile=db.query(Profile).filter(Profile.authIduser==existingUser.iduser).first();
        response_data.idprofile=userProfile.idprofile
        response_data.authIduser=userProfile.authIduser
        response_data.seedorId=userProfile.seedorId
        response_data.isValidSeedorId=userProfile.isValidSeedorId
        response_data.preferedName=userProfile.preferedName
        response_data.firstName=userProfile.firstName
        response_data.middleName=userProfile.middleName
        response_data.lastName=userProfile.lastName
        response_data.email=userProfile.email
        response_data.phone=userProfile.phone
        response_data.isPhoneVerified=userProfile.isPhoneVerified
        response_data.profileType=userProfile.profileType
        response_data.countryCode=userProfile.countryCode
        response_data.countryName=userProfile.countryName
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Valid Profile"
   
    return response_data


