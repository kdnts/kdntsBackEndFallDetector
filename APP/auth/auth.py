from fastapi import Header, HTTPException
import firebase_admin
from firebase_admin import auth

def get_current_user_id(authorization: str = Header(None)):
    print("get_current_user_id called. authorization header present:", authorization is not None)
    if not authorization:
        print("get_current_user_id: Authorization header missing")
        raise HTTPException(401, "Missing token")

    try:
        parts = authorization.split(" ")
        token = parts[1] if len(parts) > 1 else parts[0]
        print("get_current_user_id: token length:", len(token))
        decoded = auth.verify_id_token(token)
        uid = decoded.get("uid")
        print("get_current_user_id: decoded uid:", uid)
        return uid

    except Exception as e:
        print("get_current_user_id error:", type(e).__name__, e)
        raise HTTPException(401, "Invalid token")