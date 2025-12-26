from datetime import datetime
import os
import json
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.db.db import get_db, engine
from app.db.shipmentmodel import Shipment, Shipmenttracking
from app.db.models import Base
from app.schemas.schemas import ShipmentGetOUT, ShipmenttrackingNewIN, ShipmenttrackingOut, ShipmenttrackingGetIN,ShipmenttrackingGetOUT,ShipmenttrackingUpdateIN


def addShipmenttracking(payload: dict,shipmenttracking_in: ShipmenttrackingNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ShipmenttrackingOut(
        idshipmenttracking="",
        shipmentCode="",
        isActive=False,
        createdDate=datetime.now(),
        statuscode="ERROR",
        statusmessage="Invalid Shipment Tracking Object"  
    )    
    
    new_Shipmenttracking=Shipmenttracking(
        idUserSeedorId=shipmenttracking_in.userSeedorid, 
        idstatusUser=userId,
        shipmentTransitCode=shipmenttracking_in.shipmentTransitCode,
        shipmentTransitTitle=shipmenttracking_in.shipmentTransitTitle,        
        shipmenttrackingcontent=shipmenttracking_in.shipmenttrackingcontent,
        shipmentTransitSummary=shipmenttracking_in.shipmentTransitSummary,
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
        response_data.shipmentCode=new_Shipmenttracking.shipmentCode
        response_data.isActive=new_Shipmenttracking.isActive
        response_data.createdDate=new_Shipmenttracking.createdDate       
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Shipment Tracking Added Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Addition Of Shipment Tracking update failed")        

    return response_data

def updateShipmenttracking(payload: dict,shipmenttracking_in: ShipmenttrackingUpdateIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=ShipmenttrackingOut(
        idshipmenttracking="",
        shipmentCode="",
        isActive=False,
        createdDate=datetime.now(),
        statuscode="ERROR",
        statusmessage="Invalid Shipment Tracking Object"  
    )    
    
    new_Shipmenttracking=Shipmenttracking(       
        idUserSeedorId=shipmenttracking_in.userSeedorid, 
        idstatusUser=userId,
        shipmentCode=shipmenttracking_in.shipmentCode,
        shipmentTransitCode=shipmenttracking_in.shipmentTransitCode,
        shipmentTransitTitle=shipmenttracking_in.shipmentTransitTitle,        
        shipmenttrackingcontent=shipmenttracking_in.shipmenttrackingcontent,
        shipmentTransitSummary=shipmenttracking_in.shipmentTransitSummary,
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
        response_data.shipmentCode=new_Shipmenttracking.shipmentCode
        response_data.isActive=new_Shipmenttracking.isActive
        response_data.createdDate=new_Shipmenttracking.createdDate       
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Shipment Tracking Updated Successfully"
    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Shipment Tracking Update Failed")        

    return response_data

def getShipmenttracking(payload: dict,shipmenttracking_in: ShipmenttrackingGetIN, request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    address_list=[]
    address=None

    shipmenttracking_listOut=ShipmenttrackingGetOUT(
        shipmentCode="",
        listShipmenttracking=[],   
        statuscode="ERROR",
        statusmessage="No Shipment Tracking Found" 
        )

    if shipmenttracking_in.shipmentCode :
        shipmenttracking_list=db.query(Shipmenttracking).filter(Shipmenttracking.shipmentCode == shipmenttracking_in.shipmentCode).all()
        shipmenttracking_listOut.shipmentCode =shipmenttracking_in.shipmentCode
        for tmpShipmenttracking in shipmenttracking_list:           
          shipmenttracking_listOut.listShipmenttracking.append(tmpShipmenttracking)
        shipmenttracking_listOut.statuscode="SUCCESS"
        shipmenttracking_listOut.statusmessage="Shipment Tracking Found" 

    response_data=shipmenttracking_listOut

    return response_data


