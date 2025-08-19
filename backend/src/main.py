from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from src.api.routers import auth, credentials, devices, network
from src.dependencies import get_database
from src.utils.logging import logger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Including auth router")
app.include_router(auth.router, prefix="/auth", tags=["auth"])
logger.info("Including credentials router")
app.include_router(credentials.router, prefix="/credentials", tags=["credentials"])
logger.info("Including devices router")
app.include_router(devices.router, prefix="/devices", tags=["devices"])
logger.info("Including network router")
app.include_router(network.router, prefix="/network", tags=["network"])

@app.get("/health", tags=["health"])
async def health_check(db: AsyncIOMotorClient = Depends(get_database)):
    try:
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection failed")