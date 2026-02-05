import time
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.email_security import send_notification_email
from app.db.db import SessionLocal, get_db
from app.db.mastermodel import Lov
from app.db.notification import Notification

def notification_worker():
    db = SessionLocal()
    while True:
        try:
           
            notification_list=db.query(Notification).filter(Notification.status == "ACTIVE").filter(Notification.deliveryMethod.contains("EMAIL")).filter(Notification.attributes == "PENDING").order_by(Notification.createdDate.desc()).limit(10).all()      
            for tmpnotification in notification_list:
                if "EMAIL" in tmpnotification.deliveryMethod:
                    lovTemplate=db.query(Lov).filter(Lov.lovCode == "NOTIFICATION_TEMPLATE").filter(Lov.lovKey == tmpnotification.templateCode).all()                
                    send_notification_email(tmpnotification,lovTemplate,db)
                    tmpnotification.attributes="DELIVERED"                    
                    db.commit()
                   
        except Exception as e:
            print(e)

        
        time.sleep(300)  # Sleep for 5 minutes before checking for new notifications
