import os
import json
import uuid
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.db.db import get_db, engine
from app.db.usermodel import  User,Profile
from app.db.mastermodel import Lov
from app.db.models import Base
from app.schemas.schemas import LovAddressIn, MasterDataInsertOut, UserCreate, UserOut,LoginUser,LoginOut,LovOut,LovIn,LovListItem,UserName,UserNameOut
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


def insert_countries(db: Session):
    response = requests.get(settings.REST_COUNTRIES_API_URL)
    countries = response.json()

    inserted = 0
    skipped = 0
    records_to_add = []

    for c in countries:
        lov_key = c.get("cca2")
        lov_value = c.get("name", {}).get("common")
        lov_attribute1 = c.get("flags", {}).get("png")
        lov_attribute2 = c.get("idd", {}).get("root", "") + (c.get("idd", {}).get("suffixes", [""])[0] if c.get("idd", {}).get("suffixes") else "")
        lov_attribute3 = c.get("cca3")
        lov_attribute4 =c.get("name", {}).get("common").upper().replace(" ", "_")

        if not lov_key or not lov_value:
            continue

        # Prevent duplicates
        exists = db.query(Lov).filter(
            Lov.lovCode == "COUNTRY",
            Lov.lovKey == lov_key
        ).first()

        if exists:
            skipped += 1
            continue

        record = Lov(
            lovCode="COUNTRY",
            lovKey=lov_key,
            lovValue=lov_value,
            lovAttribute1=lov_attribute1,
            lovAttribute2=lov_attribute2,
            lovAttribute3=lov_attribute3,
            lovAttribute4=lov_attribute4
        )
        records_to_add.append(record)
        inserted += 1

    # Bulk insert all new records in one commit
    if records_to_add:
        try:
            db.add_all(records_to_add)
            db.commit()
        except IntegrityError:
            db.rollback()
            # If some duplicate slipped through due to race conditions, recalc skipped
            skipped += len(records_to_add)

    response_out = MasterDataInsertOut(
        inserted=str(inserted),
        skipped=str(skipped),
        total=len(countries)
    )

    return response_out




def insert_states(db: Session):        

    lovItems = db.query(Lov).filter(Lov.lovCode == 'COUNTRY').all()   
    # lovItems=[] 
    # t1lovItem=Lov(
    #     lovCode='COUNTRY',
    #     lovKey="",  
    #     lovValue="India"

    # )
    # lovItems.append(t1lovItem)

    if not lovItems:
        raise HTTPException(status_code=400, detail="Lov Not Found")
    statescount=0
    insertedcount=0
    skippedcount=0
    for lovitem in lovItems:
        country_name = lovitem.lovValue
        response = requests.post(settings.REST_COUNTRIES_STATES_API_URL, json={"country": country_name})
        data = response.json()

        if data.get("error") or "data" not in data:
            # return {"status": "FAILED", "message": data.get("msg", "No data")}
            continue

        states = data["data"].get("states", [])
        inserted = 0
        skipped = 0
        records_to_add = []

        country_name = country_name.replace(" ", "_")

        for s in states:
            state_name = s.get("name")
            state_code = s.get("state_code")
            if not state_name:
                continue

            lov_key = state_name.upper().replace(" ", "_")

            # Prevent duplicates
            exists = db.query(Lov).filter(
                Lov.lovCode == f"STATE_{country_name.upper()}",
                Lov.lovKey == lov_key                
            ).first()

            if exists:
                skipped += 1
                continue

            record = Lov(
                idlov=str(uuid.uuid4()),
                lovCode=f"STATE_{country_name.upper()}",
                lovKey=lov_key,
                lovValue=state_name, 
                lovAttribute1 =state_code              
            )
            records_to_add.append(record)
            inserted += 1

        statescount=statescount +len(states)
        insertedcount=insertedcount + inserted
       
        # Bulk insert all new records in one commit
        if records_to_add:
            try:
                db.add_all(records_to_add)
                db.commit()
            except IntegrityError:
                db.rollback()
                # If some duplicate slipped through due to race conditions, recalc skipped
                skippedcount=skippedcount + len(records_to_add)

    response_out = MasterDataInsertOut(
        inserted=str(insertedcount),
        skipped=str(skippedcount),
        total=statescount
    )
            
    return response_out


def lookup_india_pin(lovAddressIn: LovAddressIn):
   # country_code= lovAddressIn.country_code
    postal_code= lovAddressIn.postal_code
    url = f"https://api.postalpincode.in/pincode/{postal_code}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return {"STATUS": "FAILED", "message": "No data found"}
    if not resp:
        return {"STATUS": "FAILED", "message": "No data found"}
    
    return resp.json()


def lookup_us_ca_zip(lovAddressIn: LovAddressIn):
    country_code= lovAddressIn.country_code
    country_code= country_code[:2]
    postal_code= lovAddressIn.postal_code
    url = f"https://api.zippopotam.us/{country_code}/{postal_code}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return {"STATUS": "FAILED", "message": "No data found"}
    if not resp:
        return {"STATUS": "FAILED", "message": "No data found"}
    
    return resp.json()


def lookup_other(lovAddressIn: LovAddressIn): 
    return {"STATUS": "SUCCESS", "message": "No data found"}

# Example
# data = lookup_zip("us", "90210")
# print(data)
