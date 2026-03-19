from __future__ import annotations

from pydantic import BaseModel


class PasswordResetCreate(BaseModel):
    cd_usuario: int
    email: str


class PasswordResetUpdate(BaseModel):
    cd_usuario: int
    nova_senha: str
