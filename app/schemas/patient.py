from __future__ import annotations

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, root_validator

class AddressBase(BaseModel):
    tipo: Optional[str] = None
    cep: str
    cidade: str
    bairro: str
    logradouro: str
    uf: str
    numero: str
    complemento: Optional[str] = None
    cd_responsavel: Optional[int] = None

class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    cd_endereco: Optional[int] = None

class ResponsibleBase(BaseModel):
    cpf: str
    nome: str
    dt_nascimento: str

class ResponsibleCreate(ResponsibleBase):
    pass

class ResponsibleUpdate(ResponsibleBase):
    cd_responsavel: Optional[int] = None

class PatientBase(BaseModel):
    nm_paciente: str
    dt_nasc: str
    sexo: str
    cd_genero: int
    tip_sang: str
    cd_perfil: int

class PatientCreate(PatientBase):
    cd_usuario: int
    responsavel: Optional[List[ResponsibleCreate]] = None
    endereco_paciente: Optional[AddressCreate] = None
    endereco_responsavel: Optional[AddressCreate] = None

class PatientUpdate(BaseModel):
    nm_paciente: Optional[str] = None
    dt_nasc: Optional[str] = None
    sexo: Optional[str] = None
    cd_genero: Optional[int] = None
    tip_sang: Optional[str] = None
    cd_perfil: Optional[int] = None
    ativo: Optional[str] = None

class PatientResponse(PatientBase):
    cd_paciente: int
    ativo: str
    nm_genero: Optional[str] = None
    perfil: Optional[str] = None
    responsavel: Optional[List[dict]] = None
    enderecos: Optional[List[dict]] = None
