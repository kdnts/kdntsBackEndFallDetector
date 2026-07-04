from fastapi import Header, HTTPException
import firebase_admin
from firebase_admin import auth

def get_current_user_id(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing token")
    
    try:
        token = authorization.split(" ")[1]
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    
    except Exception:
        raise HTTPException(401, "Invalid token")