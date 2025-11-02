import os
import json
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.db.db import get_db, engine
from app.db.models import Base, Shipmenttracking
from app.schemas.schemas import ShipmenttrackingNewIN, ShipmenttrackingOut, ShipmenttrackingGetIN,ShipmenttrackingGetOUT,ShipmenttrackingUpdateIN


def addShipmenttracking(payload: dict,shipmenttracking_in: ShipmenttrackingNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ShipmenttrackingOut(
        idshipmenttracking="",
        shipmenttrackingStatus="",
        statuscode="ERROR",
        statusmessage="Invalid Shipmenttracking Object"  
    )    
    
    new_Shipmenttracking=Shipmenttracking(
        idshipment=shipmenttracking_in.idshipment,
        shipmentCode=shipmenttracking_in.shipmentCode,
        shipmentTransitCode=shipmenttracking_in.shipmentTransitCode,
        shipmentTransitTitle=shipmenttracking_in.shipmentTransitTitle,
        shipmenttrackingcontent=shipmenttracking_in.shipmenttrackingcontent,
        shipmentTransitDetail=shipmenttracking_in.shipmentTransitDetail,
        isActive=True,
        createdBy = userId,
        updatedBy = userId    
    )
       
    try:
        db.add(new_Shipmenttracking)
        db.commit()
        db.refresh(new_Shipmenttracking) 
        response_data.idshipmenttracking=new_Shipmenttracking.idshipmenttracking
        response_data.shipmenttrackingStatus=new_Shipmenttracking.shipmenttrackingStatus
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Shipmenttracking Added Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Address update failed")        

    return response_data

def updateShipmenttracking(payload: dict,shipmenttracking_in: ShipmenttrackingUpdateIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ShipmenttrackingOut(
        idshipmenttracking=None,
        shipmenttrackingStatus=None,
        statuscode="ERROR",
        statusmessage="Invalid Shipmenttracking Object"  
        )
    
    new_Shipmenttracking=None
    if shipmenttracking_in.idshipmenttracking :
        new_Shipmenttracking = db.query(Shipmenttracking).filter(Shipmenttracking.idshipmenttracking == shipmenttracking_in.idaddress).first()
   
    new_Shipmenttracking.shipmenttrackingStatus=shipmenttracking_in.shipmenttrackingStatus,
    new_Shipmenttracking.createdBy = userId,
    new_Shipmenttracking.updatedBy = userId    
    try:
        db.commit()
        db.refresh(new_Shipmenttracking) 
        response_data.idshipmenttracking=new_Shipmenttracking.idshipmenttracking
        response_data.shipmenttrackingStatus=new_Shipmenttracking.shipmenttrackingStatus
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Shipmenttracking Updated Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Shipmenttracking Update Failed")        

    return response_data

def getShipmenttracking(payload: dict,shipmenttracking_in: ShipmenttrackingGetIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    shipmenttracking_listOut=ShipmenttrackingGetOUT(
        idUser=None,
        listAddress=None,
        statuscode="ERROR",
        statusmessage="No Address Found" 
        )

    if shipmenttracking_in.idaddress :
        shipmenttracking = db.query(Shipmenttracking).filter(Shipmenttracking.idaddress == shipmenttracking_in.idaddress).first()
        shipmenttracking_listOut.idUser=userId
        shipmenttracking_listOut.listShipmenttracking.append(shipmenttracking)
        statuscode="SUCCESS"
        statusmessage="Address Found" 
    else:
        shipmenttracking_list=db.query(Shipmenttracking).filter(Shipmenttracking.idUser == userId).all()
        shipmenttracking_listOut.idUser=userId
        for tmpShipmenttracking in shipmenttracking_list:            
            shipmenttracking_listOut.listShipmenttracking.append(tmpShipmenttracking)
        statuscode="SUCCESS"
        statusmessage="Address Found" 

    response_data=shipmenttracking_listOut

    return response_data
