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
from app.db.shipmentmodel import Shipment
from app.db.models import Base
from app.schemas.schemas import ShipmentNewIN, ShipmentOut, ShipmentGetIN,ShipmentGetOUT,ShipmentUpdateIN


def addShipment(payload: dict,shipment_in: ShipmentNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ShipmentOut(
        idshipment=None,
        isActive=None,
        statuscode="ERROR",
        statusmessage="Invalid shipment Object"  
    )    

    tmp_count= db.query(func.count(Shipment.idUser)).filter(Shipment.idUser == userId).scalar()
    if not tmp_count or tmp_count==0:
        tmp_count=1
    else:
        tmp_count=tmp_count+1

    profile=db.query(Profile).filter(Profile.idprofile == profileId).first() 

    tmp_seedorId=profile.seedorId
    tmp_Code="SH"
    
    new_shipment=Shipment(
        shipmentCode=tmp_seedorId+"/"+tmp_Code+"/"+str(tmp_count),
        idUser=userId,
        label="SHIPMENT",
        shipperId= shipment_in.shipperId,
        shipperName= shipment_in.shipperName,
        description= shipment_in.description,
        isActive=True,
        createdBy = userId,
        updatedBy = userId    
    )
    try:
        db.add(new_shipment)
        db.commit()
        db.refresh(new_shipment) 
        response_data.idshipment=new_shipment.idshipment
        response_data.isActive=new_shipment.isActive
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
        isActive=False,
        statuscode="ERROR",
        statusmessage="Invalid shipment Object"  
        )
    
 
    if shipment_in.idshipment :
        new_shipment = db.query(Shipment).filter(Shipment.idshipment == shipment_in.idshipment).first()
   
    new_shipment.isActive=shipment_in.isActive,
    new_shipment.createdBy = userId,
    new_shipment.updatedBy = userId    
    try:
        db.commit()
        db.refresh(new_shipment) 
        response_data.idshipment=new_shipment.idshipment
        response_data.shipmentStatus=new_shipment.shipmentStatus
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="shipment Updated Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="shipment Update Failed")        

    return response_data

def getShipment(payload: dict,shipment_in: ShipmentGetIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]   
   

    shipment_listOut=ShipmentGetOUT(
        listShipment=[],
        statuscode="ERROR",
        statusmessage="No Shipment Found" 
        )

    if shipment_in.idshipment :
        shipment = db.query(Shipment).filter(Shipment.shipmentCode == shipment_in.shipmentCode).first()
        shipment_listOut.listShipment.append(shipment)
        statuscode="SUCCESS"
        statusmessage="Shipment Found" 
    else:
        shipment_list=db.query(Shipment).filter(Shipment.idUser == userId).all()        
        for tmpshipment in shipment_list:            
            shipment_listOut.listshipment.append(tmpshipment)
        shipment_listOut.statuscode="SUCCESS"
        shipment_listOut.statusmessage="Shipment Found" 

    response_data=shipment_listOut

    return response_data
