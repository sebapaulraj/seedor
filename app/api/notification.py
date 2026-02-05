import os
import json
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.db.accessmodel import Access
from app.db.consentmodel import ConsentRequest,Consent
from app.db.db import get_db, engine
from app.db.addressmodel import Address
from app.db.notification import Notification
from app.db.usermodel import Profile
from app.db.agreementmodel import Agreement
from app.db.shipmentmodel import Shipment
from app.db.models import Base
from app.api.consentrequest import validateConsentItem
from app.schemas.notificationschema import NotificationModel, NotificationOut, NotificationRequestIN, NotificationRequestNewIN

def validateItemType(itemType: str):
    valid_types=["ADDRESS","AGREEMENT","SHIPMENT"]
    if itemType not in valid_types:
        raise HTTPException(status_code=400, detail="Item Type Not Valid")
    return True

def validateDeliveryMethod(deliveryMethod: str):
    valid_types=["EMAIL","SMS","PUSH"]
    
    methods = [m.strip() for m in deliveryMethod.split(",")]

    invalid = [m for m in methods if m not in valid_types]

    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid delivery methods: {invalid}"
        )

    return True


def validateNotificationType(notificationType: str):
    valid_types=["ALERT","INFO","ERROR"]
    if notificationType not in valid_types:
        raise HTTPException(status_code=400, detail="Notification Type Not Valid")
    return True

def UpdateNotificationDelivery(payload: dict,notificationRequestNewIN_in: NotificationRequestIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="Notification Delivery Failed"
    )   
    new_notification=db.query(Notification).filter(Notification.idnotification == notificationRequestNewIN_in.idnotification).filter(Notification.receiverIdUser == userId).first()
    if new_notification is None:
        raise HTTPException(status_code=400, detail="Notification Not Found")

    try:        
        new_notification.deliveryStatus="DELIVERED"
        db.commit()
        db.refresh(new_notification) 
        response_data.listnotification.append(new_notification)
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Notification Delivered Successfully"

    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Notification Failed")        

    return response_data


def UpdateNotificationAllSeedoridDelivery(payload: dict,request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="Notification Delivery Failed"
    ) 
   
    new_notifications=db.query(Notification).filter(Notification.receiverIdUser == userId).filter(Notification.deliveryMethod.contains('PUSH')).filter(Notification.deliveryStatus == 'PENDING').all()
    if new_notifications is None:
        raise HTTPException(status_code=400, detail="Notification Not Found")

    try: 
        for new_notification in new_notifications:             
            new_notification.deliveryStatus="DELIVERED"           
            db.commit()
            db.refresh(new_notification) 
            response_data.listnotification.extend(new_notifications)
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Notification Delivered Successfully"

    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Notification Failed")        

    return response_data

def UpdateNotificationReadReceipt(payload: dict,notificationRequestNewIN_in: NotificationRequestIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="Notification Read Failed"
    )   
    new_notification=db.query(Notification).filter(Notification.idnotification == notificationRequestNewIN_in.idnotification).filter(Notification.receiverIdUser == userId).first()
    if new_notification is None:
        raise HTTPException(status_code=400, detail="Notification Not Found")

    try:        
        new_notification.deliveryStatus="DELIVERED"
        new_notification.readingStatus="READ"
        db.commit()
        db.refresh(new_notification) 
        response_data.listnotification.append(new_notification)
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Notification Read Successfully"

    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Notification Failed")        

    return response_data

def UpdateNotificationDelete(payload: dict,notificationRequestNewIN_in: NotificationRequestIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="Notification Delete Failed"
    )   
    new_notification=db.query(Notification).filter(Notification.idnotification == notificationRequestNewIN_in.idnotification).first()
    if new_notification is None:
        raise HTTPException(status_code=400, detail="Notification Not Found")

    try:        
        new_notification.status="DELETED"       
        db.commit()
        db.refresh(new_notification) 
        response_data.listnotification.append(new_notification)
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Notification Deleted Successfully"

    except IntegrityError as e:            
        db.rollback()
        raise HTTPException(status_code=400, detail="Notification Failed")        

    return response_data

def createNotification(payload: dict,notificationRequestNewIN_in: NotificationRequestNewIN, request: Request, db: Session = Depends(get_db)):
    # ensure unique email (handled by DB unique constraint but check to return friendly message)
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
    
    response_data=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="Notification Creation Failed"
    )   
    if notificationRequestNewIN_in.senderSeedorId is None:
        sendorUserid=userId
        senderSeedorid=db.query(Profile).filter(Profile.idprofile == profileId).first().seedorId
    else:
        sendorUserid=db.query(Profile).filter(Profile.seedorId == notificationRequestNewIN_in.senderSeedorId).first().authIduser
        if sendorUserid is None:
            raise HTTPException(status_code=400, detail="Sender SeedorId Not Valid")
        senderSeedorid=notificationRequestNewIN_in.senderSeedorId
    receiverIduser=db.query(Profile).filter(Profile.seedorId == notificationRequestNewIN_in.receiverSeedorId).first().authIduser
    if receiverIduser is None:
        raise HTTPException(status_code=400, detail="Receiver SeedorId Not Valid")
    
    validateNotificationType(notificationRequestNewIN_in.notificationType)
    validateDeliveryMethod(notificationRequestNewIN_in.deliveryMethod)
    new_notification=Notification(
        senderIdUser=sendorUserid,
        senderSeedorId=senderSeedorid,
        receiverIdUser=receiverIduser,
        receiverSeedorId=notificationRequestNewIN_in.receiverSeedorId,
        itemType=notificationRequestNewIN_in.itemType,
        notificationType=notificationRequestNewIN_in.notificationType,
        templateCode=notificationRequestNewIN_in.templateCode,
        deliveryMethod=notificationRequestNewIN_in.deliveryMethod,
        messageTitle=notificationRequestNewIN_in.messageTitle if notificationRequestNewIN_in.messageTitle else "",
        messageSubject=notificationRequestNewIN_in.messageSubject if notificationRequestNewIN_in.messageSubject else "",
        messagebody=notificationRequestNewIN_in.messagebody if notificationRequestNewIN_in.messagebody else "",
        attributes=notificationRequestNewIN_in.attributes,
        deliveryStatus="PENDING",
        readingStatus="UNREAD",
        status="ACTIVE"
    )

    try:        
        db.add(new_notification)
       # db.add(new_consent)
        db.commit()
        db.refresh(new_notification) 
        response_data.listnotification.append(new_notification)
        response_data.statuscode="SUCCESS"
        response_data.statusmessage="Notification Created Successfully"

    except IntegrityError as e:  
        print(e)          
        db.rollback()
        raise HTTPException(status_code=400, detail="Notification Failed")        

    return response_data



def getNotificationAllSender(payload: dict,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    notification_listOut=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="No Notification Found" 
        )

    notification_list=db.query(Notification).filter(Notification.senderIdUser == userId).filter(Notification.status == "ACTIVE").order_by(Notification.createdDate.desc()).all()      
    for tmpnotification in notification_list: 
        tmpnotificationBaseModel=NotificationModel(
            idnotification=tmpnotification.idnotification,
            senderIdUser=tmpnotification.senderIdUser,
            senderSeedorId=tmpnotification.senderSeedorId,
            receiverIdUser=tmpnotification.receiverIdUser,
            receiverSeedorId=tmpnotification.receiverSeedorId,
            itemType=tmpnotification.itemType,
            notificationType=tmpnotification.notificationType,
            templateCode=tmpnotification.templateCode,
            deliveryMethod=tmpnotification.deliveryMethod,
            messageTitle=tmpnotification.messageTitle if tmpnotification.messageTitle else "",
            messageSubject=tmpnotification.messageSubject if tmpnotification.messageSubject else "",
            messagebody=tmpnotification.messagebody if tmpnotification.messagebody else "",
            deliveryStatus=tmpnotification.deliveryStatus,
            readingStatus=tmpnotification.readingStatus,           
            createdDate=str(tmpnotification.createdDate),
            status=tmpnotification.status
            
        )           
        notification_listOut.listnotification.append(tmpnotificationBaseModel)
    notification_listOut.statuscode="SUCCESS"
    notification_listOut.statusmessage="Notification Found" 

    response_data=notification_listOut

    return response_data


def getNotificationAllReceiver(payload: dict,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    notification_listOut=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="No Notification Found" 
        )

    notification_list=db.query(Notification).filter(Notification.receiverIdUser == userId).filter(Notification.status == "ACTIVE").order_by(Notification.createdDate.desc()).all()      
    for tmpnotification in notification_list: 
        tmpnotificationBaseModel=NotificationModel(
            idnotification=tmpnotification.idnotification,
            senderIdUser=tmpnotification.senderIdUser,
            senderSeedorId=tmpnotification.senderSeedorId,
            receiverIdUser=tmpnotification.receiverIdUser,
            receiverSeedorId=tmpnotification.receiverSeedorId,
            itemType=tmpnotification.itemType,
            notificationType=tmpnotification.notificationType,
            templateCode=tmpnotification.templateCode,
            deliveryMethod=tmpnotification.deliveryMethod,
            messageTitle=tmpnotification.messageTitle if tmpnotification.messageTitle else "",
            messageSubject=tmpnotification.messageSubject if tmpnotification.messageSubject else "",
            messagebody=tmpnotification.messagebody if tmpnotification.messagebody else "",
            deliveryStatus=tmpnotification.deliveryStatus,
            readingStatus=tmpnotification.readingStatus,           
            createdDate=str(tmpnotification.createdDate),
            status=tmpnotification.status
            
        )           
        notification_listOut.listnotification.append(tmpnotificationBaseModel)
    notification_listOut.statuscode="SUCCESS"
    notification_listOut.statusmessage="Notification Found" 

    response_data=notification_listOut

    return response_data


def getNotificationAllReceiverById(payload: dict,notificationRequestNewIN_in: NotificationRequestIN,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    notification_listOut=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="No Notification Found" 
        )

    notification_list=db.query(Notification).filter(Notification.idnotification == notificationRequestNewIN_in.idnotification).filter(Notification.receiverIdUser == userId).order_by(Notification.createdDate.desc()).all()      
    for tmpnotification in notification_list: 
        tmpnotificationBaseModel=NotificationModel(
            idnotification=tmpnotification.idnotification,
            senderIdUser=tmpnotification.senderIdUser,
            senderSeedorId=tmpnotification.senderSeedorId,
            receiverIdUser=tmpnotification.receiverIdUser,
            receiverSeedorId=tmpnotification.receiverSeedorId,
            itemType=tmpnotification.itemType,
            notificationType=tmpnotification.notificationType,
            templateCode=tmpnotification.templateCode,
            deliveryMethod=tmpnotification.deliveryMethod,
            messageTitle=tmpnotification.messageTitle if tmpnotification.messageTitle else "",
            messageSubject=tmpnotification.messageSubject if tmpnotification.messageSubject else "",
            messagebody=tmpnotification.messagebody if tmpnotification.messagebody else "",
            deliveryStatus=tmpnotification.deliveryStatus,
            readingStatus=tmpnotification.readingStatus,           
            createdDate=str(tmpnotification.createdDate),
            status=tmpnotification.status
            
        )           
        notification_listOut.listnotification.append(tmpnotificationBaseModel)
    notification_listOut.statuscode="SUCCESS"
    notification_listOut.statusmessage="Notification Found" 

    response_data=notification_listOut

    return response_data


def getNotificationAllReceiverByDeliveryStatus(payload: dict,notificationRequestNewIN_in: NotificationRequestIN,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    notification_listOut=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="No Notification Found" 
        )

    notification_list=db.query(Notification).filter(Notification.deliveryStatus == notificationRequestNewIN_in.deliveryStatus).filter(Notification.receiverIdUser == userId).order_by(Notification.createdDate.desc()).all()      
    for tmpnotification in notification_list: 
        tmpnotificationBaseModel=NotificationModel(
            idnotification=tmpnotification.idnotification,
            senderIdUser=tmpnotification.senderIdUser,
            senderSeedorId=tmpnotification.senderSeedorId,
            receiverIdUser=tmpnotification.receiverIdUser,
            receiverSeedorId=tmpnotification.receiverSeedorId,
            itemType=tmpnotification.itemType,
            notificationType=tmpnotification.notificationType,
            templateCode=tmpnotification.templateCode,
            deliveryMethod=tmpnotification.deliveryMethod,
            messageTitle=tmpnotification.messageTitle if tmpnotification.messageTitle else "",
            messageSubject=tmpnotification.messageSubject if tmpnotification.messageSubject else "",
            messagebody=tmpnotification.messagebody if tmpnotification.messagebody else "",
            deliveryStatus=tmpnotification.deliveryStatus,
            readingStatus=tmpnotification.readingStatus,           
            createdDate=str(tmpnotification.createdDate),
            status=tmpnotification.status
            
        )           
        notification_listOut.listnotification.append(tmpnotificationBaseModel)
    notification_listOut.statuscode="SUCCESS"
    notification_listOut.statusmessage="Notification Found" 

    response_data=notification_listOut

    return response_data



def getNotificationAllReceiverByReadingStatus(payload: dict,notificationRequestNewIN_in: NotificationRequestIN,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    notification_listOut=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="No Notification Found" 
        )

    notification_list=db.query(Notification).filter(Notification.readingStatus == notificationRequestNewIN_in.readingStatus).filter(Notification.receiverIdUser == userId).order_by(Notification.createdDate.desc()).all()      
    for tmpnotification in notification_list: 
        tmpnotificationBaseModel=NotificationModel(
            idnotification=tmpnotification.idnotification,
            senderIdUser=tmpnotification.senderIdUser,
            senderSeedorId=tmpnotification.senderSeedorId,
            receiverIdUser=tmpnotification.receiverIdUser,
            receiverSeedorId=tmpnotification.receiverSeedorId,
            itemType=tmpnotification.itemType,
            notificationType=tmpnotification.notificationType,
            templateCode=tmpnotification.templateCode,
            deliveryMethod=tmpnotification.deliveryMethod,
            messageTitle=tmpnotification.messageTitle if tmpnotification.messageTitle else "",
            messageSubject=tmpnotification.messageSubject if tmpnotification.messageSubject else "",
            messagebody=tmpnotification.messagebody if tmpnotification.messagebody else "",
            deliveryStatus=tmpnotification.deliveryStatus,
            readingStatus=tmpnotification.readingStatus,           
            createdDate=str(tmpnotification.createdDate),
            status=tmpnotification.status
            
        )           
        notification_listOut.listnotification.append(tmpnotificationBaseModel)
    notification_listOut.statuscode="SUCCESS"
    notification_listOut.statusmessage="Notification Found" 

    response_data=notification_listOut

    return response_data


def getNotificationAllSenderById(payload: dict,notificationRequestNewIN_in: NotificationRequestIN,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    notification_listOut=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="No Notification Found" 
        )

    notification_list=db.query(Notification).filter(Notification.idnotification == notificationRequestNewIN_in.idnotification).filter(Notification.senderIdUser == userId).order_by(Notification.createdDate.desc()).all()      
    for tmpnotification in notification_list: 
        tmpnotificationBaseModel=NotificationModel(
            idnotification=tmpnotification.idnotification,
            senderIdUser=tmpnotification.senderIdUser,
            senderSeedorId=tmpnotification.senderSeedorId,
            receiverIdUser=tmpnotification.receiverIdUser,
            receiverSeedorId=tmpnotification.receiverSeedorId,
            itemType=tmpnotification.itemType,
            notificationType=tmpnotification.notificationType,
            templateCode=tmpnotification.templateCode,
            deliveryMethod=tmpnotification.deliveryMethod,
            messageTitle=tmpnotification.messageTitle if tmpnotification.messageTitle else "",
            messageSubject=tmpnotification.messageSubject if tmpnotification.messageSubject else "",
            messagebody=tmpnotification.messagebody if tmpnotification.messagebody else "",
            deliveryStatus=tmpnotification.deliveryStatus,
            readingStatus=tmpnotification.readingStatus,           
            createdDate=str(tmpnotification.createdDate),
            status=tmpnotification.status
            
        )           
        notification_listOut.listnotification.append(tmpnotificationBaseModel)
    notification_listOut.statuscode="SUCCESS"
    notification_listOut.statusmessage="Notification Found" 

    response_data=notification_listOut

    return response_data


def getNotificationAllSenderByDeliveryStatus(payload: dict,notificationRequestNewIN_in: NotificationRequestIN,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    notification_listOut=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="No Notification Found" 
        )

    notification_list=db.query(Notification).filter(Notification.deliveryStatus == notificationRequestNewIN_in.deliveryStatus).filter(Notification.senderIdUser == userId).order_by(Notification.createdDate.desc()).all()      
    for tmpnotification in notification_list: 
        tmpnotificationBaseModel=NotificationModel(
            idnotification=tmpnotification.idnotification,
            senderIdUser=tmpnotification.senderIdUser,
            senderSeedorId=tmpnotification.senderSeedorId,
            receiverIdUser=tmpnotification.receiverIdUser,
            receiverSeedorId=tmpnotification.receiverSeedorId,
            itemType=tmpnotification.itemType,
            notificationType=tmpnotification.notificationType,
            templateCode=tmpnotification.templateCode,
            deliveryMethod=tmpnotification.deliveryMethod,
            messageTitle=tmpnotification.messageTitle if tmpnotification.messageTitle else "",
            messageSubject=tmpnotification.messageSubject if tmpnotification.messageSubject else "",
            messagebody=tmpnotification.messagebody if tmpnotification.messagebody else "",
            deliveryStatus=tmpnotification.deliveryStatus,
            readingStatus=tmpnotification.readingStatus,           
            createdDate=str(tmpnotification.createdDate),
            status=tmpnotification.status
            
        )           
        notification_listOut.listnotification.append(tmpnotificationBaseModel)
    notification_listOut.statuscode="SUCCESS"
    notification_listOut.statusmessage="Notification Found" 

    response_data=notification_listOut

    return response_data



def getNotificationAllSenderByReadingStatus(payload: dict,notificationRequestNewIN_in: NotificationRequestIN,request: Request, db: Session = Depends(get_db)):
    userId=payload["userid"]
    profileId=payload["profileId"]
    email=payload["email"]    
   

    notification_listOut=NotificationOut(
        listnotification=[],
        statuscode="ERROR",
        statusmessage="No Notification Found" 
        )

    notification_list=db.query(Notification).filter(Notification.readingStatus == notificationRequestNewIN_in.readingStatus).filter(Notification.senderIdUser == userId).order_by(Notification.createdDate.desc()).all()      
    for tmpnotification in notification_list: 
        tmpnotificationBaseModel=NotificationModel(
            idnotification=tmpnotification.idnotification,
            senderIdUser=tmpnotification.senderIdUser,
            senderSeedorId=tmpnotification.senderSeedorId,
            receiverIdUser=tmpnotification.receiverIdUser,
            receiverSeedorId=tmpnotification.receiverSeedorId,
            itemType=tmpnotification.itemType,
            notificationType=tmpnotification.notificationType,
            templateCode=tmpnotification.templateCode,
            deliveryMethod=tmpnotification.deliveryMethod,
            messageTitle=tmpnotification.messageTitle if tmpnotification.messageTitle else "",
            messageSubject=tmpnotification.messageSubject if tmpnotification.messageSubject else "",
            messagebody=tmpnotification.messagebody if tmpnotification.messagebody else "",
            deliveryStatus=tmpnotification.deliveryStatus,
            readingStatus=tmpnotification.readingStatus,           
            createdDate=str(tmpnotification.createdDate),
            status=tmpnotification.status
            
        )           
        notification_listOut.listnotification.append(tmpnotificationBaseModel)
    notification_listOut.statuscode="SUCCESS"
    notification_listOut.statusmessage="Notification Found" 

    response_data=notification_listOut

    return response_data