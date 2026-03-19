from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel

class MedicalRecordBase(BaseModel):
    cd_paciente: int
    dt_prontuario: str
    txt_prontuario: str

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordUpdate(BaseModel):
    cd_paciente: Optional[int] = None
    dt_prontuario: Optional[str] = None
    txt_prontuario: Optional[str] = None

class MedicalRecordResponse(MedicalRecordBase):
    cd_prontuario: int
