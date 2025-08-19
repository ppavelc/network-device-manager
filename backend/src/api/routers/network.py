from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.dependencies import get_current_user, get_database
from src.utils.logging import logger

router = APIRouter(tags=["network"])

@router.get("/info", tags=["network"])
async def get_network_info(current_user=Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Retrieve network information for all devices.
    """
    try:
        devices = await db["devices"].find().to_list(None)
        network_info = [{"name": dev["name"], "ip": dev["ip"]} for dev in devices]
        logger.info("Retrieved network info")
        return {"network_info": network_info, "count": len(network_info)}
    except Exception as e:
        logger.error(f"Error retrieving network info: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve network info")