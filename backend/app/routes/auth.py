from fastapi import APIRouter, HTTPException

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

    user_id = register_user(
        data.loginId,
        data.password
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

    token = authenticate_user(
        data.loginId,
        data.password
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