from email.mime.multipart import MIMEMultipart
import re
import smtplib
from typing import List
import aiosmtplib
from email.mime.text import MIMEText

from fastapi import Depends
from pytest import Session
from app.core.config import settings
from app.db.db import get_db
from app.db.mastermodel import Lov
from app.db.usermodel import Profile
from app.schemas.notificationschema import NotificationModel

def send_verification_email(to_email: str, token: str):
        """
        Send password reset email via Gmail.
        
        Args:
            to_email: Recipient's email address
            reset_url: The complete reset URL with token
        """
        verify_link = f"{settings.FRONTEND_VERIFY_URL}?token={token}"
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Password Reset Request'
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = to_email
        
        # Email body (HTML and plain text versions)
        text_body = f"""
        Hello,
        
        You requested a password reset. Click the link below to reset your password:
        
        {verify_link}
        
        This link will expire in 30 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Your App Team
        """
        
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #4A90E2;">Password Reset Request</h2>
            <p>Hello,</p>
            <p>You requested a password reset. Click the button below to reset your password:</p>
            <p style="margin: 30px 0;">
              <a href="{verify_link}" 
                 style="background-color: #4A90E2; color: white; padding: 12px 24px; 
                        text-decoration: none; border-radius: 4px; display: inline-block;">
                Reset Password
              </a>
            </p>
            <p><small>Or copy and paste this link: {verify_link}</small></p>
            <p style="color: #E74C3C;"><strong>This link will expire in 30 minutes.</strong></p>
            <p>If you didn't request this, please ignore this email.</p>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="color: #888; font-size: 12px;">Best regards,<br>Seedor</p>
          </body>
        </html>
        """
        
        # Attach both versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via Gmail SMTP
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
                server.send_message(msg)
            print(f"Password reset email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
        

def send_notification_email(tmpNotificationModel: NotificationModel,lovTemplate: List[Lov],db: Session = Depends(get_db)):
        
        lovDict = {}
        if lovTemplate:
          for lov in lovTemplate:
              lovDict[lov.lovValue] = lov.lovAttribute1

        myprofil=db.query(Profile).filter(Profile.authIduser == tmpNotificationModel.receiverIdUser).first()
        if not myprofil or not myprofil.email:
            print(f"No valid profile or email found for user ID {tmpNotificationModel.receiverIdUser}")
            return False
        if is_valid_email(myprofil.email) is False:
            print(f"Invalid email format for user ID {tmpNotificationModel.receiverIdUser}: {myprofil.email}")
            return False
        
        if tmpNotificationModel.messageSubject is None:
            print(f"No message subject found for notification for template code  {tmpNotificationModel.templateCode}")
            return False
        
        if tmpNotificationModel.messageTitle is None:
            print(f"No message title found for notification for template code  {tmpNotificationModel.templateCode}")
            return False

        if tmpNotificationModel.messagebody is None:
            print(f"No message body found for notification for template code  {tmpNotificationModel.templateCode}")
            return False
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = tmpNotificationModel.messageSubject
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = myprofil.email

        # Email body (HTML and plain text versions)
        text_body = tmpNotificationModel.messagebody 
                
        
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #4A90E2;">{tmpNotificationModel.messageSubject}</h2>
            <p>Hello,</p>
            <p>{tmpNotificationModel.messageTitle}</p>
            <p style="margin: 30px 0;">
              {tmpNotificationModel.messagebody}
            </p>
            <p>If you didn't request this, please ignore this email.</p>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="color: #888; font-size: 12px;">Best regards,<br>Seedor</p>
          </body>
        </html>
        """
        if lovDict:
            email_text_body = text_body.format(**lovDict)
            email_html_body = html_body.format(**lovDict)
        else:
            email_text_body = text_body
            email_html_body = html_body

        # Attach both versions
        part1 = MIMEText(email_text_body, 'plain')
        part2 = MIMEText(email_html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via Gmail SMTP
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
                server.send_message(msg)
            print(f"Notification email sent successfully to {myprofil.email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
        
def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))