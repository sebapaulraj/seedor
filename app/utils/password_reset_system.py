import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import re
from datetime import datetime

class PasswordResetManager:
    def __init__(self, secret_key, gmail_user, gmail_app_password):
        """
        Initialize the password reset manager.
        
        Args:
            secret_key: Secret key for token generation (keep this secure!)
            gmail_user: Your Gmail address
            gmail_app_password: Gmail app password (not your regular password)
        """
        self.secret_key = secret_key
        self.gmail_user = gmail_user
        self.gmail_app_password = gmail_app_password
        self.serializer = URLSafeTimedSerializer(secret_key)
    
    def validate_email(self, email):
        """Verify email format is valid."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def generate_reset_token(self, email):
        """Generate a secure token for password reset."""
        return self.serializer.dumps(email, salt='password-reset-salt')
    
    def verify_reset_token(self, token, max_age=1800):
        """
        Verify the reset token and extract email.
        
        Args:
            token: The reset token to verify
            max_age: Token expiry time in seconds (default 1800 = 30 minutes)
        
        Returns:
            email if valid, None if expired or invalid
        """
        try:
            email = self.serializer.loads(
                token,
                salt='password-reset-salt',
                max_age=max_age
            )
            return email
        except SignatureExpired:
            print("Token has expired")
            return None
        except BadSignature:
            print("Invalid token")
            return None
    
    def send_reset_email(self, to_email, reset_url):
        """
        Send password reset email via Gmail.
        
        Args:
            to_email: Recipient's email address
            reset_url: The complete reset URL with token
        """
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Password Reset Request'
        msg['From'] = self.gmail_user
        msg['To'] = to_email
        
        # Email body (HTML and plain text versions)
        text_body = f"""
        Hello,
        
        You requested a password reset. Click the link below to reset your password:
        
        {reset_url}
        
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
              <a href="{reset_url}" 
                 style="background-color: #4A90E2; color: white; padding: 12px 24px; 
                        text-decoration: none; border-radius: 4px; display: inline-block;">
                Reset Password
              </a>
            </p>
            <p><small>Or copy and paste this link: {reset_url}</small></p>
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
                server.login(self.gmail_user, self.gmail_app_password)
                server.send_message(msg)
            print(f"Password reset email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    def request_password_reset(self, email, base_url):
        """
        Complete password reset flow: validate email, generate token, send email.
        
        Args:
            email: User's email address
            base_url: Your app's base URL (e.g., 'https://yourapp.com/reset-password')
        
        Returns:
            True if successful, False otherwise
        """
        # Step 1: Verify email format
        if not self.validate_email(email):
            print("Invalid email format")
            return False
        
        # Step 2: Generate token (expires in 30 minutes)
        token = self.generate_reset_token(email)
        
        # Step 3: Prepare reset URL
        reset_url = f"{base_url}?token={token}"
        
        # Step 4: Send email
        return self.send_reset_email(email, reset_url)


# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    # Configuration (KEEP THESE SECURE!)
    SECRET_KEY = "your-secret-key-here-change-this"  # Use a strong random key
    GMAIL_USER = "your-email@gmail.com"
    GMAIL_APP_PASSWORD = "your-app-password"  # Not your regular Gmail password!
    
    # Initialize the manager
    reset_manager = PasswordResetManager(SECRET_KEY, GMAIL_USER, GMAIL_APP_PASSWORD)
    
    # ---- Scenario 1: User requests password reset ----
    user_email = "user@example.com"
    base_url = "https://yourapp.com/reset-password"
    
    print("Sending password reset email...")
    success = reset_manager.request_password_reset(user_email, base_url)
    
    if success:
        print("✓ Reset email sent successfully!")
    
    # ---- Scenario 2: User clicks the link and you verify the token ----
    # (In real app, extract token from URL query parameter)
    example_token = reset_manager.generate_reset_token(user_email)
    
    print("\nVerifying token from reset link...")
    verified_email = reset_manager.verify_reset_token(example_token)
    
    if verified_email:
        print(f"✓ Token valid! Allow password reset for: {verified_email}")
        # Here you would show the password reset form
    else:
        print("✗ Token invalid or expired")
        # Show error message to user
