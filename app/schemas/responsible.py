from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class ResponsibleCreate(BaseModel):
    cpf: str
    nome: str
    dt_nascimento: str


class ResponsibleUpdate(BaseModel):
    cpf: Optional[str] = None
    nome: Optional[str] = None
    dt_nascimento: Optional[str] = None
