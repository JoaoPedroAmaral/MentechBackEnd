from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class AddressCreate(BaseModel):
    tipo: Optional[str] = "PACIENTE"
    cep: str
    cidade: str
    bairro: str
    logradouro: str
    uf: str
    numero: str
    complemento: Optional[str] = None
    cd_responsavel: Optional[int] = None


class AddressUpdate(BaseModel):
    tipo: Optional[str] = None
    cep: Optional[str] = None
    cidade: Optional[str] = None
    bairro: Optional[str] = None
    logradouro: Optional[str] = None
    uf: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    cd_responsavel: Optional[int] = None
