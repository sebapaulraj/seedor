from email.mime.multipart import MIMEMultipart
import smtplib
import aiosmtplib
from email.mime.text import MIMEText
from app.core.config import settings

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
            <p style="color: #888; font-size: 12px;">Best regards,<br>Your App Team</p>
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