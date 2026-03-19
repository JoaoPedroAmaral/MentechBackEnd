from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, validator

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserCreate(BaseModel):
    nm_usuario: str
    email: str
    cip: str
    senha: str
    confirmar_senha: Optional[str] = None

    @validator("email")
    def validate_email(cls, value: str) -> str:
        if not EMAIL_RE.match(value):
            raise ValueError("Invalid email")
        return value


class UserUpdate(BaseModel):
    nm_usuario: Optional[str] = None
    email: Optional[str] = None
    cip: Optional[str] = None

    @validator("email")
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value and not EMAIL_RE.match(value):
            raise ValueError("Invalid email")
        return value
