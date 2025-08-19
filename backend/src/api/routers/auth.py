from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.dependencies import get_database
from src.utils.logging import logger
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from typing import Dict

router = APIRouter(tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str

SECRET_KEY = "your-secret-key"  # Must match dependencies.py
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        user = await db["users"].find_one({"username": request.username})
        if not user or user["password"] != request.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        token = jwt.encode(
            {
                "sub": request.username,
                "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        logger.info(f"User {request.username} logged in successfully")
        return {"token": token}
    except Exception as e:
        logger.error(f"Error in login: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")