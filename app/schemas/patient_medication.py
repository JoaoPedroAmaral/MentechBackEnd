from pydantic import BaseModel, Field
from typing import Optional

class PatientMedicationCreate(BaseModel):
    cd_paciente: int
    cd_medicamento: int
    dias_ministracao: str = Field(..., max_length=150)
    dose: str = Field(..., max_length=100)

class PatientMedicationUpdate(BaseModel):
    cd_paciente: Optional[int] = None
    cd_medicamento: Optional[int] = None
    dias_ministracao: Optional[str] = Field(None, max_length=150)
    dose: Optional[str] = Field(None, max_length=100)
