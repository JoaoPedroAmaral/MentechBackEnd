from __future__ import annotations
from pydantic import BaseModel, validator
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class LoginRequest(BaseModel):
    email: str
    password: str

    @validator("email")
    def validate_email(cls, value: str) -> str:
        if not EMAIL_RE.match(value):
            raise ValueError("Invalid email format")
        return value

class LoginResponse(BaseModel):
    cd_usuario: int
    nm_usuario: str
    email: str
    cip: str
