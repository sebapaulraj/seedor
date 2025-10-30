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
from app.db.models import Base, Shipment
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
    
    new_shipment=Shipment(
        idshipment=userId,
        label= shipment_in.label,
        offerorSeedorId= shipment_in.offerorSeedorId,
        signatorySeedorId= shipment_in.signatorySeedorId,
        itemType= shipment_in.itemType,
        itemId=shipment_in.itemId, 
        status=shipment_in.status,
        isActive=True,
        createdBy = userId,
        updatedBy = userId    
    )
       
    try:
        db.commit()
        db.refresh(new_shipment) 
        response_data.idshipment=new_shipment.idshipment
        response_data.isActive=new_shipment.isActive
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="shipment Added Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Address update failed")        

    return response_data

def updateShipment(payload: dict,shipment_in: ShipmentUpdateIN, request: Request, db: Session = Depends(get_db)):
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
    
    new_shipment=None
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
    address_list=[]
    address=None

    shipment_listOut=ShipmentGetOUT(
        idUser=None,
        listAddress=None,
        statuscode="ERROR",
        statusmessage="No Address Found" 
        )

    if shipment_in.idaddress :
        shipment = db.query(shipment).filter(shipment.idaddress == shipment_in.idaddress).first()
        shipment_listOut.idUser=userId
        shipment_listOut.listshipment.append(shipment)
        statuscode="SUCCESS"
        statusmessage="Address Found" 
    else:
        shipment_list=db.query(shipment).filter(shipment.idUser == userId).all()
        shipment_listOut.idUser=userId
        for tmpshipment in shipment_list:            
            shipment_listOut.listshipment.append(tmpshipment)
        statuscode="SUCCESS"
        statusmessage="Address Found" 

    response_data=shipment_listOut

    return response_data
