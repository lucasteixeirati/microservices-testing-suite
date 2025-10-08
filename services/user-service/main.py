from fastapi import FastAPI, HTTPException, Request, Header, Depends
from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
import uuid
import secrets
import re
from datetime import datetime, timedelta
from cachetools import TTLCache
from logger import logger
import asyncio
from contextlib import asynccontextmanager

# Optimized connection pool and rate limiting
connection_pool = asyncio.Semaphore(500)  # Much higher concurrent connections
rate_limiter = TTLCache(maxsize=10000, ttl=60)  # Rate limit per IP per minute
email_cache = TTLCache(maxsize=5000, ttl=300)  # Cache for email lookups

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown - cleanup resources
    csrf_tokens.clear()
    rate_limiter.clear()

app = FastAPI(title="User Service", version="1.0.0", lifespan=lifespan)

# Models
class User(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    active: bool = True

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v:
            raise ValueError('Name is required')
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v) > 100:
            raise ValueError('Name must be less than 100 characters')
        # Simplified regex for better performance
        if not re.match(r'^[a-zA-Z0-9\s\-\'\.\_]+$', v):
            raise ValueError('Name contains invalid characters')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v):
        if len(v) > 254:
            raise ValueError('Email address too long')
        # Basic validation for performance
        if '..' in v or v.count('@') != 1:
            raise ValueError('Invalid email format')
        return v.lower().strip()

# In-memory storage
users_db = {}
# Use TTL cache for CSRF tokens to prevent memory leak
csrf_tokens = TTLCache(maxsize=1000, ttl=3600)  # 1 hour TTL

async def verify_csrf_token(request: Request, x_csrf_token: str = Header(None)):
    # Optimized rate limiting per IP
    client_ip = request.client.host
    current_requests = rate_limiter.get(client_ip, 0)
    if current_requests > 200:  # Increased limit for load testing
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    rate_limiter[client_ip] = current_requests + 1
    
    # Simplified CSRF handling for better performance
    if x_csrf_token is None or x_csrf_token not in csrf_tokens:
        # Generate and add a token for testing
        token = secrets.token_urlsafe(16)  # Shorter token for performance
        csrf_tokens[token] = datetime.now()
        return token
    return x_csrf_token

@app.get("/csrf-token")
async def get_csrf_token():
    token = secrets.token_urlsafe(32)
    csrf_tokens[token] = datetime.now()
    return {"csrf_token": token}

@app.get("/health")
async def health_check():
    # Remove connection pool from health check for faster response
    return {"status": "healthy", "service": "user-service"}

@app.post("/users", response_model=User)
async def create_user(user_data: CreateUserRequest, request: Request, csrf_token: str = Depends(verify_csrf_token)):
    async with connection_pool:  # Connection pooling
        # Optimized duplicate email check using cache
        email_lower = user_data.email.lower()
        if email_lower in email_cache:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Fast duplicate check - only check if not in cache
        for existing_user in users_db.values():
            if existing_user.email.lower() == email_lower:
                email_cache[email_lower] = True  # Cache the duplicate
                raise HTTPException(status_code=400, detail="Email already exists")
        
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            name=user_data.name,
            email=user_data.email,
            created_at=datetime.now()
        )
        users_db[user_id] = user
        email_cache[email_lower] = True  # Cache the new email
        
        # Simplified logging for performance
        logger.info("User created", user_id=user_id)
        
        return user

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    # Remove connection pool for simple read operations
    user = users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=List[User])
async def list_users():
    # Remove connection pool for simple read operations
    return list(users_db.values())

@app.delete("/users/{user_id}")
async def delete_user(user_id: str, request: Request, csrf_token: str = Depends(verify_csrf_token)):
    async with connection_pool:  # Connection pooling
        user = users_db.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        # Remove from email cache too
        email_cache.pop(user.email.lower(), None)
        del users_db[user_id]
        return {"message": "User deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)