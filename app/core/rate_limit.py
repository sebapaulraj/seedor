import time
from fastapi import HTTPException, Request
from app.core.config import settings
from collections import defaultdict

# naive in-memory rate limiter (resets on process restart)
# For production use: Redis, Cloud Memorystore, or API Gateway / Cloud Armor
VISIT_STORE = defaultdict(list)
WINDOW = 60  # seconds

def check_rate_limit(request: Request):
    client_ip = request.client.host or "unknown"
    now = time.time()
    window_start = now - WINDOW
    visits = VISIT_STORE[client_ip]
    # remove old entries
    while visits and visits[0] < window_start:
        visits.pop(0)
    if len(visits) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Too many requests")
    visits.append(now)
    VISIT_STORE[client_ip] = visits
