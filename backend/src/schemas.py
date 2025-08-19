from pydantic import BaseModel, Field
from pydantic.networks import IPv4Address
from typing import List, Optional, Dict, Any

class Credentials(BaseModel):
    username: str
    password: str

class CredentialsResponse(BaseModel):
    user_id: str
    username: str

class DecryptedCredentials(BaseModel):
    username: str
    password: str

class CredentialsListResponse(BaseModel):
    credentials: List[str]
    count: int

class DeleteCredentialsResponse(BaseModel):
    deleted_count: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Device(BaseModel):
    name: str
    ip: IPv4Address
    device_type: str = Field(..., example="cisco_ios")
    username: str
    password: str

class DeviceDetail(BaseModel):
    device_id: str
    name: str
    ip: str
    device_type: str
    username: str
    identified_type: Optional[str] = "unknown"
    model: Optional[str] = "unknown"
    version: Optional[str] = "unknown"

class DeviceResponse(BaseModel):
    device_id: str
    name: str
    ip: str
    device_type: str
    username: str

class DeviceListResponse(BaseModel):
    devices: List[DeviceDetail]
    count: int

class DeleteDeviceResponse(BaseModel):
    deleted_count: int

class ExecuteCommands(BaseModel):
    commands: List[str]

class ExecuteResponse(BaseModel):
    output: Dict[str, Dict[str, Any]]