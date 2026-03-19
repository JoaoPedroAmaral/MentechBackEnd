from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

class PatientDisorderLink(BaseModel):
    cd_paciente: int
    cd_transtorno: int
    datas: Optional[str] = None

class PatientDisorderUpdate(BaseModel):
    datas: str
