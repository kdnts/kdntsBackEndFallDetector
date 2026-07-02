from pydantic import BaseModel

class PairDeviceRequest(BaseModel):
    deviceId: str
    devicePassword: str

class UnpairDeviceRequest(BaseModel):
    userId: str
    deviceId: str

class AddContactRequest(BaseModel):
    userId: str
    name: str
    phone:str

class MarkedReadRequest(BaseModel):
    notifications: str