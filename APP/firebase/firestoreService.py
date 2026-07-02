from APP.firebase.firebaseClient import db
from firebase_admin import firestore
from config import DEVICES_COLLECTION, FALLS_COLLECTION, NOTIFICATIONS_COLLECTION, USERS_COLLECTION

def updateLocation(deviceId, lat, lng):
    try:
        docRef = db.collection(DEVICES_COLLECTION).document(deviceId)

        docRef.update({
            "lastLat": lat,
            "lastLng": lng,
            "deviceStatus": "online",
            "lastSeen": firestore.SERVER_TIMESTAMP})

        print("\nfirestore updated")
        return True

    except Exception as e:
        print("updateLocation error:", e)
        return False

def createFall(deviceId, lat, lng):
    try:
        db.collection(FALLS_COLLECTION).add({
        "deviceId": deviceId,
        "latitude": lat,
        "longitude": lng,
        "createdAt": firestore.SERVER_TIMESTAMP})

        device = getDevice(deviceId)
        userId = device.get("userId") if device is not None else None

        createNotifications(userId, deviceId)

        print("\nsaving fall")
        return True

    except Exception as e:
        print("createFall error:", e)
        return False

def getDevice(deviceId):
    doc = (
        db.collection(DEVICES_COLLECTION).document(deviceId).get()
        )

    if not doc.exists:
        return None
    
    return doc.to_dict()

def pairDevice(deviceId, userId):
    try:
        ref = db.collection(DEVICES_COLLECTION).document(deviceId)
        snap = ref.get().to_dict()

        #block overwrite owner
        if snap.get("userId") is not None:
            return False
        
        ref.update({"userId": userId})
        return True

    except Exception as e:
        print("pairDevice error:", e)
        return False

def unpairDevice(deviceId, userId):
    try:
        db.collection(DEVICES_COLLECTION).document(deviceId).update({"userId": None})
        return True

    except Exception as e:
        print("unpairDevice error:", e)
        return False

def isDeviceOwner(deviceId, userId):
    device = getDevice(deviceId)

    if device is None:
        return False
    
    return device.get("userId") == userId

def addContact(userId, name, phone):
    try:
        db.collection(USERS_COLLECTION).document(userId).collection("contacts").add({
            "name": name,
            "phone": phone
        })
        return True

    except Exception as e:
        print("addContact error:", e)
        return False

def getContact(userId):
    contacts = []

    docs = (db.collection(USERS_COLLECTION).document(userId).collection("contacts").stream())

    for doc in docs:
        data = doc.to_dict()
        data["contactId"] = doc.id

        contacts.append(data)

    return contacts

def deleteContact(userId, contactId):
    try:
        db.collection(USERS_COLLECTION).document(userId).collection("contacts").document(contactId).delete()
        return True

    except Exception as e:
        print("deleteContact error:", e)
        return False

def createNotifications(userId, deviceId):
    try:
        db.collection(NOTIFICATIONS_COLLECTION).add({
            "userId": userId,
            "deviceId": deviceId,
            "title": "Fall Detected",
            "message": f"{deviceId} detected a fall",
            "isRead": False,
            "createdAt": firestore.SERVER_TIMESTAMP
        })
        return True

    except Exception as e:
        print("createNotifications error:", e)
        return False

def getNotifications(userId):
    notifications = []

    docs = (db.collection(NOTIFICATIONS_COLLECTION).where("userId", "==", userId).stream())

    for doc in docs:
        data = doc.to_dict()
        data["notificationId"] = doc.id

        notifications.append(data)

    return notifications

def getNotification(notificationId):
    doc = (db.collection(NOTIFICATIONS_COLLECTION).document(notificationId).get())

    if not doc.exists:
        return None
    
    return doc.to_dict()

def markNotificationRead(notificationId):
    try:
        db.collection(NOTIFICATIONS_COLLECTION).document(notificationId).update({"isRead": True})
        return True

    except Exception as e:
        print("markNotificationRead error:", e)
        return False

def getUserDevice(userId):
    try:
        docs = (db.collection(DEVICES_COLLECTION).where("userId", "==", userId).limit(1).stream())

        for doc in docs:
            data = doc.to_dict()
            data["deviceId"] = doc.id
            return data
        
        return None
    except Exception as e:
        print("getUserDevice error", e)
        return None

