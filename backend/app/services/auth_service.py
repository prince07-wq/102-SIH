import os
import jwt
import bcrypt

from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError

from app.database import get_users_collection


JWT_SECRET = os.getenv("JWT_SECRET")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_token(user_id: str) -> str:
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET is not set")

    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256"
    )


def register_user(login_id: str, password: str):
    users_collection = get_users_collection()

    existing_user = users_collection.find_one({
        "loginId": login_id
    })

    if existing_user:
        return None

    hashed_password = hash_password(password)

    user = {
        "loginId": login_id,
        "password": hashed_password,
        "createdAt": datetime.utcnow()
    }

    result = users_collection.insert_one(user)

    return str(result.inserted_id)


def authenticate_user(login_id: str, password: str):
    users_collection = get_users_collection()

    user = users_collection.find_one({
        "loginId": login_id
    })

    if not user:
        return None

    if not verify_password(password, user["password"]):
        return None

    return create_token(str(user["_id"]))
