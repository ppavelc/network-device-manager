import base64
import uuid

from cryptography.fernet import Fernet
from motor.motor_asyncio import AsyncIOMotorDatabase


class PasswordEncryptor:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.keys_collection = db["credentials_keys"]

    async def generate_key(self, user_id: str):
        key = Fernet.generate_key()
        await self.keys_collection.insert_one({"user_id": user_id, "key": base64.urlsafe_b64encode(key).decode()})
        return key

    async def get_key(self, user_id: str):
        key_doc = await self.keys_collection.find_one({"user_id": user_id})
        if not key_doc:
            raise ValueError(f"Key not found for user_id: {user_id}")
        return base64.urlsafe_b64decode(key_doc["key"])

    async def encrypt(self, password: str, user_id: str = None) -> str:
        if not user_id:
            user_id = str(uuid.uuid4())
        key = await self.generate_key(user_id)
        fernet = Fernet(key)
        return fernet.encrypt(password.encode()).decode()

    async def decrypt(self, encrypted_password: str, user_id: str) -> str:
        key = await self.get_key(user_id)
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_password.encode()).decode()