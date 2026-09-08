from pydantic import BaseModel


class RegisterRequest(BaseModel):
    loginId: str
    password: str


class LoginRequest(BaseModel):
    loginId: str
    password: str


class AuthResponse(BaseModel):
    message: str
    token: str