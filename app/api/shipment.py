from datetime import datetime
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
from app.api.access import getTypeIdAccess
from app.core.config import settings
from app.db.db import get_db, engine
from app.db.usermodel import Profile
from app.db.shipmentmodel import Shipment
from app.db.models import Base
from app.schemas.schemas import AccessGetIdTypeIN, ShipmentBase, ShipmentNewIN, ShipmentOut, ShipmentGetIN,ShipmentGetOUT,ShipmentUpdateIN


def addShipment(payload: dict,shipment_in: ShipmentNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ShipmentOut(
        idshipment="",
        shipmentCode="",
        isActive=False,
        createdDate=datetime.now(),
        statuscode="ERROR",
        statusmessage="Invalid shipment Object"  
    )    

    tmp_count= db.query(func.count(Shipment.shipperId)).filter(Shipment.shipperId == userId).scalar()
    tmp_count=tmp_count+1 if tmp_count else 1
    profile=db.query(Profile).filter(Profile.idprofile == profileId).first() 
    agency=db.query(Profile).filter(Profile.seedorId == shipment_in.agencySeedorId).first()
    deleivery=db.query(Profile).filter(Profile.seedorId == shipment_in.deliverySeedorId).first()
        
    new_shipment=Shipment(
        shipmentCode=profile.seedorId+"/SH/"+str(tmp_count),
        agencyId=agency.authIduser if agency else "SEEDOR",
        label="SHIPMENT",
        shipperId= profile.authIduser,
        shipperName= profile.preferedName,
        description= shipment_in.description,
        deliveryId= deleivery.authIduser if deleivery else "SEEDOR",
        isActive=True,
        createdBy = userId,
        updatedBy = userId    
    )
    try:
        db.add(new_shipment)
        db.commit()
        db.refresh(new_shipment) 
        response_data.idshipment=new_shipment.idshipment
        response_data.shipmentCode=new_shipment.shipmentCode
        response_data.isActive=new_shipment.isActive
        response_data.createdDate=new_shipment.createdDate
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Shipment Added Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Shipment Added Failed")        

    return response_data


def updateShipment(payload: dict,shipment_in: ShipmentUpdateIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ShipmentOut(
        idshipment="",
        shipmentCode="",        
        isActive=False,
        createdDate=datetime.now(),
        statuscode="ERROR",
        statusmessage="Invalid shipment "  
        )
    
    new_shipment = db.query(Shipment).filter(Shipment.idshipment == shipment_in.idshipment).first()   
    if not new_shipment:
        raise HTTPException(status_code=404, detail="shipment not found")
    agencyUser=db.query(Profile).filter(Profile.seedorId == shipment_in.agencySeedorId).first() 
    if not agencyUser:  
        raise HTTPException(status_code=400, detail="Invalid Agency SeedorId")
    deliveryUser=db.query(Profile).filter(Profile.seedorId == shipment_in.deliverySeedorId).first()
    if not deliveryUser:  
        raise HTTPException(status_code=400, detail="Invalid Delivery SeedorId")
    
    new_shipment.agencyId=agencyUser.authIduser if agencyUser else new_shipment.agencyId,     
    new_shipment.deliveryId=deliveryUser.authIduser if deliveryUser else new_shipment.deliveryId,
    new_shipment.description=shipment_in.description if shipment_in.description else new_shipment.description,    
    new_shipment.updatedBy = userId    
    try:
        db.commit()
        db.refresh(new_shipment) 
        response_data.idshipment=new_shipment.idshipment
        response_data.shipmentCode=new_shipment.shipmentCode
        response_data.isActive=new_shipment.isActive        
        response_data.createdDate=new_shipment.createdDate
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="shipment Updated Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="shipment Update Failed")        

    return response_data

def getShipmentAgent(payload: dict,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    shipment_listOut=ShipmentGetOUT(
        listShipment=[],
        statuscode="ERROR",
        statusmessage="No Shipment Tracking Found" 
        )

    shipmenttracking_list=db.query(Shipment).filter(Shipment.agencyId == userId).order_by(Shipment.createdDate.desc()).all()
    agencyUser=db.query(Profile).filter(Profile.authIduser == userId).first()
    for tmp_Shipment in shipmenttracking_list: 
        shipperUser=db.query(Profile).filter(Profile.authIduser == tmp_Shipment.shipperId).first() 
        shipperUserseedorId=shipperUser.seedorId if shipperUser else "SEEDOR"  
        deliveryUser=db.query(Profile).filter(Profile.authIduser == tmp_Shipment.deliveryId).first() 
        deliveryUserseedorId=deliveryUser.seedorId if deliveryUser else "SEEDOR"  
        access_in=AccessGetIdTypeIN(accessTypeId=tmp_Shipment.idshipment)
        tmpresponse_data=getTypeIdAccess(payload,access_in, request, db)
        cur_Shipment=ShipmentBase(
            idshipment=tmp_Shipment.idshipment,
            shipmentCode=tmp_Shipment.shipmentCode,
            agencyId=agencyUser.seedorId,
            label=tmp_Shipment.label,
            shipperId=shipperUserseedorId,
            shipperName=tmp_Shipment.shipperName if tmp_Shipment.shipperName else "",
            description=tmp_Shipment.description if tmp_Shipment.description else "",
            deliveryId=deliveryUserseedorId,
            isActive=tmp_Shipment.isActive,
            createdBy=tmp_Shipment.createdBy,
            createdDate=tmp_Shipment.createdDate,
            updatedBy=tmp_Shipment.updatedBy,
            updatedDate=tmp_Shipment.updatedDate,
            access=tmpresponse_data.listAccess[0].accessStatus if tmpresponse_data.statuscode=="SUCCESS" else "NONE"
        )            
        shipment_listOut.listShipment.append(cur_Shipment)
    shipment_listOut.statuscode="SUCCESS"
    shipment_listOut.statusmessage="Shipment Tracking Found" 

    response_data=shipment_listOut

    return response_data

 
def getShipmentDelivery(payload: dict,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    shipment_listOut=ShipmentGetOUT(
        listShipment=[],
        statuscode="ERROR",
        statusmessage="No Shipment Tracking Found" 
        )

    shipmenttracking_list=db.query(Shipment).filter(Shipment.deliveryId == userId).order_by(Shipment.createdDate.desc()).all()
    deliveryUser=db.query(Profile).filter(Profile.authIduser == userId).first()
    for tmp_Shipment in shipmenttracking_list:
        agencyUser=db.query(Profile).filter(Profile.authIduser == tmp_Shipment.agencyId).first()
        agencyUserseedorId=agencyUser.seedorId if agencyUser else "SEEDOR"
        shipperUser=db.query(Profile).filter(Profile.authIduser == tmp_Shipment.shipperId).first()
        shipperUserseedorId=shipperUser.seedorId if shipperUser else "SEEDOR"
        access_in=AccessGetIdTypeIN(accessTypeId=tmp_Shipment.idshipment)
        tmpresponse_data=getTypeIdAccess(payload,access_in, request, db)
        cur_Shipment=ShipmentBase(
            idshipment=tmp_Shipment.idshipment,
            shipmentCode=tmp_Shipment.shipmentCode,
            agencyId=agencyUserseedorId,
            label=tmp_Shipment.label,
            shipperId=shipperUserseedorId,
            shipperName=tmp_Shipment.shipperName if tmp_Shipment.shipperName else "",
            description=tmp_Shipment.description if tmp_Shipment.description else "",
            deliveryId=deliveryUser.seedorId,
            isActive=tmp_Shipment.isActive,
            createdBy=tmp_Shipment.createdBy,
            createdDate=tmp_Shipment.createdDate,
            updatedBy=tmp_Shipment.updatedBy,
            updatedDate=tmp_Shipment.updatedDate,
            access=tmpresponse_data.listAccess[0].accessStatus if tmpresponse_data.statuscode=="SUCCESS" else "NONE"    
        )                
        shipment_listOut.listShipment.append(cur_Shipment)
    shipment_listOut.statuscode="SUCCESS"
    shipment_listOut.statusmessage="Shipment Tracking Found" 

    response_data=shipment_listOut

    return response_data


def getShipmentShipper(payload: dict,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    shipment_listOut=ShipmentGetOUT(
        listShipment=[],
        statuscode="ERROR",
        statusmessage="No Shipment Tracking Found" 
        )

    shipmenttracking_list=db.query(Shipment).filter(Shipment.shipperId == userId).order_by(Shipment.createdDate.desc()).all()
    shipperUser=db.query(Profile).filter(Profile.authIduser ==userId ).first()
    for tmp_Shipment in shipmenttracking_list:
        agencyUser=db.query(Profile).filter(Profile.authIduser == tmp_Shipment.agencyId).first()
        agencyUserseedorId=agencyUser.seedorId if agencyUser else "SEEDOR"
        deliveryUser=db.query(Profile).filter(Profile.authIduser == tmp_Shipment.deliveryId).first()
        deliveryUserseedorId=deliveryUser.seedorId if deliveryUser else "SEEDOR"
        access_in=AccessGetIdTypeIN(accessTypeId=tmp_Shipment.idshipment)
        tmpresponse_data=getTypeIdAccess(payload,access_in, request, db)
        cur_Shipment=ShipmentBase(
            idshipment=tmp_Shipment.idshipment,
            shipmentCode=tmp_Shipment.shipmentCode,
            agencyId=agencyUserseedorId,
            label=tmp_Shipment.label,
            shipperId=shipperUser.seedorId,
            shipperName=tmp_Shipment.shipperName if tmp_Shipment.shipperName else "",
            description=tmp_Shipment.description if tmp_Shipment.description else "",
            deliveryId=deliveryUserseedorId,
            isActive=tmp_Shipment.isActive,
            createdBy=tmp_Shipment.createdBy,
            createdDate=tmp_Shipment.createdDate,
            updatedBy=tmp_Shipment.updatedBy,
            updatedDate=tmp_Shipment.updatedDate,
            access=tmpresponse_data.listAccess[0].accessStatus if tmpresponse_data.statuscode=="SUCCESS" else "NONE"        
        )            
        shipment_listOut.listShipment.append(cur_Shipment)
    shipment_listOut.statuscode="SUCCESS"
    shipment_listOut.statusmessage="Shipment Tracking Found" 

    response_data=shipment_listOut

    return response_data