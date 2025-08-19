import uuid
import re
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.dependencies import get_current_user, get_database
from src.schemas import Device, DeviceResponse, DeviceListResponse, DeleteDeviceResponse, ExecuteCommands, ExecuteResponse
from src.utils.encryptor import PasswordEncryptor
from src.utils.logging import logger
from src.utils.ssh import ssh_execute_commands
from src.utils.device_identifier import identify_device_via_ssh
import ipaddress

router = APIRouter(tags=["devices"])

@router.get("/list", response_model=DeviceListResponse)
async def list_devices(current_user=Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        devices = await db["Devices"].find().to_list(length=100)
        device_list = [
            {
                "device_id": device["device_id"],
                "name": device["name"],
                "ip": device["ip"],
                "device_type": device["device_type"],
                "username": device["username"],
                "identified_type": device.get("identified_type", "unknown"),
                "model": device.get("model", "unknown"),
                "version": device.get("version", "unknown")
            }
            for device in devices
        ]
        return {"devices": device_list, "count": len(device_list)}
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list devices")

@router.post("/add/", response_model=DeviceResponse)
async def add_device(
    device: Device, current_user=Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        device_id = str(uuid.uuid4())
        encryptor = PasswordEncryptor(db)
        encrypted_password = await encryptor.encrypt(device.password, device_id)
        device_doc = {
            "device_id": device_id,
            "name": device.name,
            "ip": str(device.ip),
            "device_type": device.device_type,
            "username": device.username,
            "encrypted_password": encrypted_password,
        }
        try:
            device_info = identify_device_via_ssh(str(device.ip), device.username, device.password)
            device_doc.update({
                "identified_type": device_info["type"],
                "model": device_info["model"],
                "version": device_info["version"]
            })
        except Exception as e:
            logger.warning(f"Device identification failed for {device.name}: {e}")
            device_doc["identified_type"] = "unknown"
            device_doc["model"] = "unknown"
            device_doc["version"] = "unknown"

        await db["Devices"].insert_one(device_doc)
        await db["Credentials"].insert_one({
            "device_id": device_id,
            "username": device.username,
            "encrypted_password": encrypted_password
        })
        network_cidr = str(ipaddress.IPv4Interface(f"{device.ip}/24").network)
        await db["Networks"].update_one(
            {"network_cidr": network_cidr},
            {"$push": {"assets": {"$each": [str(device.ip)], "$sort": 1}}},
            upsert=True
        )
        logger.info(f"Added device: {device.name}")
        return {"device_id": device_id, "name": device.name, "ip": str(device.ip), "device_type": device.device_type, "username": device.username}
    except Exception as e:
        logger.error(f"Error adding device: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add device")

@router.post("/execute/{name}", response_model=ExecuteResponse)
async def execute_commands(name: str, commands: ExecuteCommands, current_user=Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        device = await db["Devices"].find_one({"name": name})
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        encryptor = PasswordEncryptor(db)
        decrypted_password = await encryptor.decrypt(device["encrypted_password"], device["device_id"])
        outputs = await ssh_execute_commands(device["ip"], device["username"], decrypted_password, commands.commands)
        return {"output": outputs}
    except Exception as e:
        logger.error(f"Error executing commands on {name}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to execute commands")

@router.delete("/{device_id}", response_model=DeleteDeviceResponse)
async def delete_device(device_id: str, current_user=Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        device = await db["Devices"].find_one({"device_id": device_id})
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        await db["Devices"].delete_one({"device_id": device_id})
        await db["Credentials"].delete_one({"device_id": device_id})
        network_cidr = str(ipaddress.IPv4Interface(f"{device['ip']}/24").network)
        await db["Networks"].update_one(
            {"network_cidr": network_cidr},
            {"$pull": {"assets": device["ip"]}}
        )
        logger.info(f"Deleted device: {device_id}")
        return {"deleted_count": 1}
    except Exception as e:
        logger.error(f"Error deleting device {device_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete device")