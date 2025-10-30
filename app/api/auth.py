from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
from fastapi import Request, HTTPException
import base64

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Truncate the password if it's longer than 72 characters
    if len(password) > 72:
        password = password[:72]    
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def verify_access_token(token: str) -> dict | None:
    """
    Verify the JWT access token.
    Returns the decoded payload if valid, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Optional: Ensure required fields exist      
        
        if "userid" not in payload:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if "profileId" not in payload:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        if "email" not in payload:
            raise HTTPException(status_code=401, detail="Authorization header missing")
              
        return payload

    except ExpiredSignatureError:
        # Token has expired
        raise HTTPException(status_code=401, detail="Authorization header missing")
    except JWTError:
        # Token invalid or tampered
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
def get_bearer_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    # Expected format: "Bearer <token>"
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme Bearer")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    return token

def manual_basic_auth(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        scheme, encoded = auth_header.split()
        if scheme.lower() != "basic":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

        decoded = base64.b64decode(encoded).decode("utf-8")
        username, password = decoded.split(":", 1)
        
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    return {"username": username, "password": password}

def verify_basic_auth( basicauthcredential : dict) -> bool :   
    try:
      
        if basicauthcredential["username"] != settings.BASIC_AUTH_USER:
             raise HTTPException(status_code=401, detail="Wrong Authorization header")
        
       
        if basicauthcredential["password"] != settings.BASIC_AUTH_PASSWORD:
            raise HTTPException(status_code=401, detail="Wrong Authorization header")
        
        verifypass=verify_password(basicauthcredential["password"],settings.BASIC_AUTH_HASH_PASSWORD)        

        if verifypass == False:
            raise HTTPException(status_code=401, detail="Wrong Authorization header")        

    except Exception:
        raise HTTPException(status_code=401, detail="Basic Auth Failed")

    return True