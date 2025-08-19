import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.dependencies import get_current_user, get_database
from src.schemas import (
    Credentials,
    CredentialsResponse,
    DecryptedCredentials,
    CredentialsListResponse,
    DeleteCredentialsResponse,
)
from src.utils.encryptor import PasswordEncryptor
from src.utils.logging import logger

router = APIRouter()


@router.post("/add/", response_model=CredentialsResponse)
async def add_credentials(
    credentials: Credentials,
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        user_id = str(uuid.uuid4())
        encryptor = PasswordEncryptor(db)
        encrypted_password = await encryptor.encrypt(credentials.password, user_id)
        credential_doc = {
            "user_id": user_id,
            "username": credentials.username,
            "encrypted_password": encrypted_password,
        }
        await db["credentials"].insert_one(credential_doc)
        logger.info(f"Added credentials for username: {credentials.username}")
        return {"user_id": user_id, "username": credentials.username}
    except Exception as e:
        logger.error(f"Error adding credentials: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add credentials")


@router.get("/get/{username}", response_model=DecryptedCredentials)
async def get_credentials(
    username: str, current_user=Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        credential = await db["credentials"].find_one({"username": username})
        if not credential:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credentials not found")
        encryptor = PasswordEncryptor(db)
        decrypted_password = await encryptor.decrypt(credential["encrypted_password"], credential["user_id"])
        return {"username": username, "password": decrypted_password}
    except ValueError as ve:
        logger.error(f"Decryption error: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error getting credentials: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get credentials")


@router.get("/list", response_model=CredentialsListResponse)
async def list_credentials(current_user=Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        credentials = await db["credentials"].find().to_list(None)
        usernames = [cred["username"] for cred in credentials]
        return {"credentials": usernames, "count": len(usernames)}
    except Exception as e:
        logger.error(f"Error listing credentials: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list credentials")


@router.delete("/delete/{username}", response_model=DeleteCredentialsResponse)
async def delete_credentials(
    username: str, current_user=Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        credential = await db["credentials"].find_one({"username": username})
        if not credential:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credentials not found")
        delete_result = await db["credentials"].delete_one({"username": username})
        await db["credentials_keys"].delete_one({"user_id": credential["user_id"]})
        logger.info(f"Deleted credentials for username: {username}")
        return {"deleted_count": delete_result.deleted_count}
    except Exception as e:
        logger.error(f"Error deleting credentials: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete credentials")