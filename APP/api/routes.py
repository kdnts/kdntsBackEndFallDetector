from fastapi import APIRouter
from fastapi import Depends

from APP.api.schema import PairDeviceRequest, UnpairDeviceRequest, AddContactRequest
from APP.firebase.firestoreService import getDevice, pairDevice, isDeviceOwner, getContact, deleteContact, getNotification, getNotifications, markNotificationRead, getUserDevice, addContact, unpairDevice
from APP.mqtt.mqttClient import publishContact

from APP.auth.auth import get_current_user_id


router = APIRouter()

@router.post("/pair-device")
def pair_device(
    request: PairDeviceRequest,
    userId: str = Depends(get_current_user_id)
    ):

    deviceId = request.deviceId.strip() 
    if not deviceId:
        return {"success": False, "message": "Device Id required"}
    

    password = request.devicePassword.strip()
    if not password:
        return {"success": False, "message": "Password required"}

    device = getDevice(deviceId)

    if device is None:
        return {"success": False, "message": "Device not found"}

    # already owned check
    if device.get("userId") is not None:
        return {"success": False, "message": "Device already paired"}

    if device.get("devicePassword") != password:
        return {"success": False, "message": "Wrong password"}
    
    result = pairDevice(
        deviceId,
        userId
    )

    if not result:
        return {"success": False, "message": "Database error"}

    return {"success": True, "data": {"message": "Device paired"}}

@router.post("/unpair-device")
def unpair_device(request: UnpairDeviceRequest):

    deviceId = request.deviceId.strip()
    if not deviceId:
        return {"success": False, "message": "Device Id required"}
    
    userId = request.userId.strip()
    if not isDeviceOwner(deviceId, userId):
        return {"success": False, "message": "Not owner"}

    result = unpairDevice(
        deviceId, 
        userId
    )

    if not result:
        return {"success": False, "message": "Database error"}

    return {"success": True, "data": {"message": "Device unpaired"}}

@router.post("/contacts")
def add_contact(
    request: AddContactRequest,
    userId: str = Depends(get_current_user_id)):

    userId = request.userId.strip()
    if not userId:
        return{"success": False, "message": "User Id required"}

    name = request.name.strip()
    if not name:
        return {"success": False, "message": "Name required"}
    
    phone = request.phone.strip()
    if not phone:
        return {"success": False, "message": "Phone required"}
        

    result = addContact(request.userId, name, phone)

    if not result:
        return {"success": False, "message": "Database error"}

    return {"success": True, "data": {"message": "Contact added"}}

@router.get("/contacts/{userId}")
def get_contact(userId):

    if not userId.strip():
        return{"success": False, "message": "User Id required"}
    
    contacts = getContact(userId)
    return {"success": True, "data": contacts}

@router.delete("/contacts/{userId}/{contactId}")
def delete_contact(userId, contactId):

    if not userId.strip():
        return{"success": False, "message": "User Id required"}
    
    if not contactId.strip():
        return{"success": False, "message": "Contact Id required"}
    
    result = deleteContact(userId, contactId)

    if not result:
        return {"success": False, "message": "Database error"}

    return {"success": True, "data": {"message": "Contact deleted"}}

@router.get("/notifications/{userId}")
def get_notifications(userId):

    if not userId.strip():
        return{"success": False, "message": "User Id required"}

    notifications = getNotifications(userId)
    return {"success": True, "data": notifications
    }

@router.post("/notifications/{notificationId}/read")
def mark_read(notificationId):

    if notificationId is None:
        return{"success": False, "message": "Noti Id not found"}

    notification = getNotification(notificationId)
    if notification is None:
        return{"success": False, "message": "Noti not found"}

    result = markNotificationRead(notificationId)

    if not result:
        return {"success": False, "message": "Database error"}

    return {"success": True, "data": {"message": "Notification marked as read"}}

@router.get("/device/user/{userId}")
def get_user_device(userId):
    if not userId.strip():
        return {"success": False, "message": "User Id required"}
    device = getUserDevice(userId)

    if device is None:
        return {"success": False, "message": "No device paired"}
    
    return {"success": True, "data": device}

@router.post("contacts/sync")
def sync_contact(userId: str = Depends(get_current_user_id)):

    #get contacts from firestore
    contacts = getContact(userId)

    if not contacts:
        return {"success": False, "message": "No contacts found"}

    #get device
    device = getUserDevice(userId)

    if device is None:
        return {"success": False, "message": "No device found"}

    deviceId = device["deviceId"]

    #extract phones
    phones = []

    for c in contacts:
        phone = c.get("phone")
        if phone:
            phone.append(phone)

    #publish MQTT
    result = publishContact(deviceId, phones)

    if not result:
        return {"success": False, "message": "MQTT publish failed"}

    return {"success": True,"data": {"message": "Contacts synced","count": len(phones)}}