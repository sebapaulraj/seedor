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
from app.db.mastermodel import Lov
from app.db.models import Base
from app.schemas.schemas import EmailOut
from app.api.auth import hash_password, create_access_token, verify_password,verify_access_token,get_bearer_token,manual_basic_auth,verify_basic_auth
from app.core.rate_limit import check_rate_limit
from email_validator import validate_email, EmailNotValidError
from app.core.email_security import send_verification_email
from app.utils.emailauth_utils import create_email_token, verify_email_token
from app.api.user import registerUser,validateUserName,validateLogin
from app.api.master import getLov

def sendPasswordRestEmail(payload: dict, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]
    response_data=EmailOut(
        statuscode="ERROR",
        statusmessage="Error Sending Email"
    )    
    try:
        send_verification_email(email, create_email_token(email))
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Email Send Successfully"
    except Exception as e:
        raise HTTPException(status_code=400, detail="Profile update failed")

    return response_data