import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

service_account = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT"))

cred = credentials.Certificate(service_account)

firebase_admin.initialize_app(cred)

db = firestore.client()

print("firebase connected")