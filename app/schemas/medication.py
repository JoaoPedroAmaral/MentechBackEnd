from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

class MedicationBase(BaseModel):
    nm_medicamento: str = Field(..., min_length=3, max_length=100)
    dosagem: str = Field(..., min_length=1, max_length=100)
    forma_farmaceutica: Optional[str] = Field(None, max_length=100)
    principio_ativo: Optional[str] = Field(None, max_length=100)
    fabricante: Optional[str] = Field(None, max_length=100)

class MedicationCreate(MedicationBase):
    pass

class MedicationUpdate(BaseModel):
    nm_medicamento: Optional[str] = Field(None, min_length=3, max_length=100)
    dosagem: Optional[str] = Field(None, min_length=1, max_length=100)
    forma_farmaceutica: Optional[str] = None
    principio_ativo: Optional[str] = None
    fabricante: Optional[str] = None

class MedicationResponse(MedicationBase):
    cd_medicamento: int

    model_config = {"from_attributes": True}

class PrescriptionCreate(BaseModel):
    cd_paciente: int
    cd_medicamento: int
    dias_ministracao: str = Field(..., max_length=150)
    dose: str = Field(..., max_length=100)

class PrescriptionUpdate(BaseModel):
    dias_ministracao: Optional[str] = Field(None, max_length=150)
    dose: Optional[str] = Field(None, max_length=100)
