from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def create_email_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=15)
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def verify_email_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None
