from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest
)

from app.services.auth_service import (
    register_user,
    authenticate_user
)


router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


@router.post("/register")
def register(data: RegisterRequest):
    try:
        user_id = register_user(
            data.loginId,
            data.password
        )
    except (PyMongoError, RuntimeError):
        raise HTTPException(
            status_code=503,
            detail="Authentication service is temporarily unavailable"
        )

    if user_id is None:
        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )

    return {
        "message": "Account created successfully",
        "user_id": user_id
    }


@router.post("/login")
def login(data: LoginRequest):
    try:
        token = authenticate_user(
            data.loginId,
            data.password
        )
    except (PyMongoError, RuntimeError):
        raise HTTPException(
            status_code=503,
            detail="Authentication service is temporarily unavailable"
        )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid login ID or password"
        )

    return {
        "message": "Login successful",
        "token": token
    }
