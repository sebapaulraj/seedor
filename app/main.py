import os
import json
from fastapi import FastAPI, Depends, HTTPException, status, Request,WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.access import getAccessById, getHistoryAccess, getHistoryAccessAll, getTypeIdAccess,grandAccess, revokeAccess
from app.api.address import addAddress, deleteAddress,getAddressesAll, getAddressesId, updateAddress
from app.api.agreement import addAgreement, deleteAgreement,getAgreementAll, getAgreementId, updateAgreement
from app.core.config import settings
from app.api.consent import acceptConsentOffer, acceptConsentRequest, createConsentOffer, createConsentRequest,  getConsentOfferdAll, getConsentOfferdId,  getConsentSignedAll, getConsentSignedId, rejectConsentOffer, rejectConsentRequest
from app.db.db import get_db, engine
from app.db.usermodel import User,Profile
from app.db.mastermodel import Lov
from app.db.models import Base
from app.schemas.consentschema import ConsentGetIN, ConsentGetOUT, ConsentRequestNewIN, ConsentRequestOut, ConsentUpdateIN
from app.schemas.schemas import AccessGetIdIN, AccessGetIdTypeIN, AccessNewIN, AccessOut, AddressDeleteIN, AddressGetIN, AddressGetOUT, AddressNewIN, AddressOut, AddressUpdateIN, AgreementDeleteIN, AgreementGetIN, AgreementNewIN, AgreementOut, AgreementUpdateIN,ShipmentNewIN, ShipmentOut, ShipmentUpdateIN, ShipmenttrackingGetIN, ShipmenttrackingNewIN, ShipmenttrackingOut, ShipmenttrackingUpdateIN, UserCreate, UserOut,LoginUser,LoginOut,LovOut,LovIn,UserName,UserNameOut,UserProfile,UserProfileOut,ValidateSeedorId,ValidateSeedorIdOut
from app.api.auth import create_access_token,verify_access_token,get_bearer_token,manual_basic_auth,verify_basic_auth
from app.core.rate_limit import check_rate_limit
from email_validator import validate_email, EmailNotValidError
from app.core.email_security import send_verification_email
from app.utils.emailauth_utils import create_email_token, verify_email_token
from app.api.shipment import addShipment, getShipment, updateShipment
from app.api.shipmenttracking import addShipmenttracking, getShipmenttracking, getShipmenttrackingAll, updateShipmenttracking
from app.api.user import registerUser,validateUserName,validateLogin
from app.api.master import getLov
from app.api.userprofile import updateProfile,validateSeedorId
from app.api.resetPassword import sendPasswordRestEmail

# Create DB tables (run once or via migrations in prod — Alembic recommended)
#Base.metadata.create_all(bind=engine)

app = FastAPI(title="Seedor Information Seeding API")
active_connections = {}
# CORS - restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none';"
        response.headers["Permissions-Policy"] = "interest-cohort=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)

@app.exception_handler(IntegrityError)
async def db_integrity_exception_handler(request: Request, exc: IntegrityError):
    # Prevent leaking DB details
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database integrity error."},
    )


@app.websocket("/seedor/1.0/ws/{actor_id}")
async def websocket_endpoint(websocket: WebSocket, actor_id: str):
    await websocket.accept()
    active_connections[actor_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except:
        del active_connections[actor_id]


#------- authentication block starts -------------
@app.post("/seedor/1.0/auth/register", response_model=UserOut, status_code=201)
async def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    verify_basic_auth(manual_basic_auth(request))
    # Rate limit check (basic)
    #check_rate_limit(request)
    response_data=registerUser(user_in,request,db)
    token=""    
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = token
    return response

@app.get("/seedor/1.0/auth/userName", response_model=UserNameOut, status_code=201)
async def userName(userName_in: UserName, request: Request, db: Session = Depends(get_db)):
    verify_basic_auth(manual_basic_auth(request))    
    token=""
    response_data=validateUserName(userName_in,request,db)    
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response


@app.post("/seedor/1.0/auth/login", response_model=LoginOut, status_code=201)
async def login(login_in: LoginUser, request: Request, db: Session = Depends(get_db)):
    verify_basic_auth(manual_basic_auth(request))        
    response_data=validateLogin(login_in,request,db)   
    token = ""
    if(response_data.idprofile!=0):
        token = create_access_token({"userid": str(response_data.authIduser),"profileId":response_data.idprofile, "email": response_data.email})  
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/auth/reset", response_model=LovOut, status_code=201)
async def reset(lov_in: LovIn, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=sendPasswordRestEmail(payload, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

#------- authentication block ends -------------

#------- profile block started -------------
@app.put("/seedor/1.0/profile/update", response_model=UserProfileOut, status_code=201)
async def profileUpdte(userProfile_in: UserProfile, request: Request, db: Session = Depends(get_db)):
    token=get_bearer_token(request)
    payload=verify_access_token(token)     
    response_data=updateProfile(payload,userProfile_in,request,db)       
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/profile/seedorid", response_model=ValidateSeedorIdOut, status_code=201)
async def valSeedorId(validateSeedorId_in: ValidateSeedorId, request: Request, db: Session = Depends(get_db)):
    token=get_bearer_token(request)
    payload=verify_access_token(token)     
    response_data=validateSeedorId(payload,validateSeedorId_in,request,db)       
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response
#------- profile block ends -------------

#------- master block started -------------
@app.get("/seedor/1.0/master/lov", response_model=LovOut, status_code=201)
async def lov(lov_in: LovIn, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getLov(lov_in,request,db) 
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

#------- master block ends -------------

#------- access block started -------------
@app.post("/seedor/1.0/access/grand", response_model=AccessOut, status_code=201)
async def accessGrand(access_in: AccessNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=grandAccess(payload,access_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.post("/seedor/1.0/access/revoke", response_model=AccessOut, status_code=201)
async def accessRevoke(access_in: AccessNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=revokeAccess(payload,access_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response


@app.get("/seedor/1.0/access/id", response_model=AccessOut, status_code=201)
async def accessGetId(access_in: AccessGetIdIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getAccessById(payload,access_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/access/type", response_model=AccessOut, status_code=201)
async def accessGetTypeId(access_in: AccessGetIdTypeIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getTypeIdAccess(payload,access_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/access/history", response_model=AccessOut, status_code=201)
async def accessGetHistory(access_in: AccessGetIdTypeIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getHistoryAccess(payload,access_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/access", response_model=AccessOut, status_code=201)
async def accessGetHistoryAll(request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getHistoryAccessAll(payload,request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response



#------- access block ends -------------

#------- address block started -------------
@app.post("/seedor/1.0/address/add", response_model=AddressOut, status_code=201)
async def addressAdd(address_in: AddressNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=addAddress(payload,address_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.put("/seedor/1.0/address/update", response_model=AccessOut, status_code=201)
async def addressUpdate(address_in: AddressUpdateIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=updateAddress(payload,address_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response


@app.get("/seedor/1.0/address/id", response_model=AddressGetOUT, status_code=201)
async def addressesGet(address_in: AddressGetIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getAddressesId(payload,address_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/address", response_model=AddressGetOUT, status_code=201)
async def addressesGet(request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getAddressesAll(payload,request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.delete("/seedor/1.0/address/id", response_model=AddressDeleteIN, status_code=201)
async def addressDelete(address_in: AddressGetIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=deleteAddress(payload,address_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

#------- address block ends -------------


#------- agreement block started -------------
@app.post("/seedor/1.0/agreement/add", response_model=AgreementOut, status_code=201)
async def agreementAdd(agreement_in: AgreementNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=addAgreement(payload,agreement_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.put("/seedor/1.0/agreement/update", response_model=AgreementOut, status_code=201)
async def agreementUpdate(agreement_in: AgreementUpdateIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=updateAgreement(payload,agreement_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response


@app.get("/seedor/1.0/agreement/id", response_model=AgreementOut, status_code=201)
async def agreementGet(agreement_in: AgreementGetIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getAgreementId(payload,agreement_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/agreement", response_model=AgreementOut, status_code=201)
async def agreementGet(request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getAgreementAll(payload, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.delete("/seedor/1.0/agreement/id", response_model=AgreementOut, status_code=201)
async def agreementDelete(address_in: AgreementDeleteIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=deleteAgreement(payload,address_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

#------- agreement block ends -------------

#------- consent block started -------------
@app.post("/seedor/1.0/consent/request", response_model=ConsentRequestOut, status_code=201)
async def consentRequestCreate(consent_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=createConsentRequest(payload,consent_in, request, db)
    itemOwner_id = response_data.itemOwnerIdUser
    if itemOwner_id in active_connections:
        await active_connections[response_data.itemOwnerIdUser].send_json({"msg":response_data.dict()})
        response_data.isactiveConnection=True
        response_data.consentSendStatus="Consent Requested"
    
    response = JSONResponse(status_code=200, content=jsonable_encoder(response_data))
    response.headers["X-Access-Token"] = str(token)
    return response

@app.post("/seedor/1.0/consent/offer", response_model=ConsentRequestOut, status_code=201)
async def consentRequestOffer(consent_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=createConsentOffer(payload,consent_in, request, db)
    itemBeneficiary_id = response_data.itemBeneficiaryIdUser
    if itemBeneficiary_id in active_connections:
        await active_connections[response_data.itemBeneficiaryIdUser].send_json({"msg":response_data.dict()})
        response_data.isactiveConnection=True
        response_data.consentSendStatus="Consent Requested"
    
    response = JSONResponse(status_code=200, content=jsonable_encoder(response_data))
    response.headers["X-Access-Token"] = str(token)
    return response

@app.put("/seedor/1.0/consent/request", response_model=ConsentRequestOut, status_code=201)
async def consentRequestAcceptRequest(consent_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=acceptConsentRequest(payload,consent_in, request, db)
    response = JSONResponse(status_code=200, content=jsonable_encoder(response_data))
    response.headers["X-Access-Token"] = str(token)
    return response

@app.put("/seedor/1.0/consent/offer", response_model=ConsentRequestOut, status_code=201)
async def consentRequestAcceptOffer(consent_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=acceptConsentOffer(payload,consent_in, request, db)
    response = JSONResponse(status_code=200, content=jsonable_encoder(response_data))
    response.headers["X-Access-Token"] = str(token)
    return response


@app.delete("/seedor/1.0/consent/request", response_model=ConsentRequestOut, status_code=201)
async def consentRejectRequestReject(consent_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=rejectConsentRequest(payload,consent_in, request, db)
    response = JSONResponse(status_code=200, content=jsonable_encoder(response_data))
    response.headers["X-Access-Token"] = str(token)
    return response

@app.delete("/seedor/1.0/consent/offer", response_model=ConsentRequestOut, status_code=201)
async def consentRejectRequestOffer(consent_in: ConsentRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=rejectConsentOffer(payload,consent_in, request, db)
    response = JSONResponse(status_code=200, content=jsonable_encoder(response_data))
    response.headers["X-Access-Token"] = str(token)
    return response


@app.get("/seedor/1.0/consent/offered/id", response_model=ConsentRequestOut, status_code=201)
async def consentGetOfferedId(consent_in: ConsentGetIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getConsentOfferdId(payload,consent_in, request, db)
    response = JSONResponse(status_code=200, content=jsonable_encoder(response_data))
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/consent/offered", response_model=ConsentGetOUT, status_code=201)
async def consentGetOfferdAll(request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getConsentOfferdAll(payload,request, db)
    response = JSONResponse(status_code=200, content=jsonable_encoder(response_data))
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/consent/signed/id", response_model=ConsentRequestOut, status_code=201)
async def consentGetSignedId(consent_in: ConsentGetIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getConsentSignedId(payload,consent_in, request, db)
    response = JSONResponse(status_code=200, content=jsonable_encoder(response_data))
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/consent/signed", response_model=ConsentGetOUT, status_code=201)
async def consentGetSignedAll(request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getConsentSignedAll(payload,request, db)
    response = JSONResponse(status_code=200, content=jsonable_encoder(response_data))
    response.headers["X-Access-Token"] = str(token)
    return response

#------- consent block ends -------------

'''
#------- shipment block started -------------
@app.post("/seedor/1.0/shipment/add", response_model=ShipmentOut, status_code=201)
async def shipmentAdd(shipment_in: ShipmentNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=addShipment(payload,shipment_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.put("/seedor/1.0/shipment/update", response_model=ShipmentOut, status_code=201)
async def shipmentUpdate(shipment_in: ShipmentUpdateIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=updateShipment(payload,shipment_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response


@app.get("/seedor/1.0/shipment", response_model=ShipmentOut, status_code=201)
async def shipmentGet(shipment_in: ShipmentUpdateIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getShipment(payload,shipment_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

#------- shipment block ends -------------

'''

#------- shipmenttracking block started -------------
@app.post("/seedor/1.0/shipment/add", response_model=ShipmenttrackingOut, status_code=201)
async def shipmenttrackingAdd(shipmenttracking_in: ShipmenttrackingNewIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=addShipmenttracking(payload,shipmenttracking_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.put("/seedor/1.0/shipment/update", response_model=ShipmenttrackingOut, status_code=201)
async def shipmenttrackingUpdate(shipmenttracking_in: ShipmenttrackingUpdateIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=updateShipmenttracking(payload,shipmenttracking_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response


@app.get("/seedor/1.0/shipment/code", response_model=ShipmenttrackingOut, status_code=201)
async def shipmenttrackingGet(shipmenttracking_in: ShipmenttrackingGetIN, request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getShipmenttracking(payload,shipmenttracking_in, request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response

@app.get("/seedor/1.0/shipment/items", response_model=ShipmenttrackingOut, status_code=201)
async def shipmenttrackingGetAll(request: Request, db: Session = Depends(get_db)):
    # Rate limit check (basic)
    #check_rate_limit(request)
    token=get_bearer_token(request)
    payload=verify_access_token(token)
    response_data=getShipmenttrackingAll(payload,request, db)
    response = JSONResponse(status_code=200, content=response_data.dict())
    response.headers["X-Access-Token"] = str(token)
    return response


#------- shipmenttracking block ends -------------

# Health check
@app.get("/seedor/1.0/health")
def health():    
    return {"status": "ok"}
