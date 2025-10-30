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
from app.schemas.schemas import UserCreate, UserOut,LoginUser,LoginOut,LovOut,LovIn,LovListItem,UserName,UserNameOut
from app.api.auth import hash_password, create_access_token, verify_password,verify_access_token,get_bearer_token,manual_basic_auth,verify_basic_auth
from app.core.rate_limit import check_rate_limit
from email_validator import validate_email, EmailNotValidError
from app.core.email_security import send_verification_email
from app.utils.emailauth_utils import create_email_token, verify_email_token
from app.api.user import registerUser,validateUserName,validateLogin

def getLov(lov_in: LovIn, request: Request, db: Session = Depends(get_db)):
   
    lovItems = db.query(Lov).filter(Lov.lovCode == lov_in.lovCode).all()    
    if not lovItems:
        raise HTTPException(status_code=400, detail="Lov Not Found")
     
    response_data = LovOut(
        idlov="",
        lovCode="",
        lovlist= [],
        statuscode="ERROR",
        statusmessage="Invalid LOV Code"        
        )
  
    # Return user (without token in body); token could be returned or sent via secure cookie/HTTP-only cookie
    if lovItems:
        lovitemfirst=lovItems[1]
        response_data.idlov=lovitemfirst.idlov
        response_data.lovCode=lovitemfirst.lovCode       
        for lovitem in lovItems:
            lovListItem=LovListItem(
                lovKey=lovitem.lovKey,
                lovValue=lovitem.lovKey,
                lovAttribute1=lovitem.lovAttribute1,
                lovAttribute2=lovitem.lovAttribute2,
                lovAttribute3=lovitem.lovAttribute3,
                lovAttribute4=lovitem.lovAttribute4,
                lovAttribute5=lovitem.lovAttribute5,
            )
            response_data.lovlist.append(lovListItem)
        response_data.statuscode="SUCCESS",
        response_data.statusmessage="Valid LOV"
    return response_data