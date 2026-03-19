from typing import Optional
from pydantic import BaseModel, Field

class ActivityCreate(BaseModel):
    cd_meta: int
    nm_atividade: str = Field(..., min_length=5, max_length=100)
    descricao_atividade: str = Field(..., min_length=5, max_length=2000)
    dt_atividade: str
    parecer_tecnico: str = Field(..., min_length=5, max_length=5000)
    resultado: str = Field(..., max_length=50)

class ActivityUpdate(BaseModel):
    nm_atividade: Optional[str] = Field(None, min_length=5, max_length=100)
    descricao_atividade: Optional[str] = Field(None, min_length=5, max_length=2000)
    dt_atividade: Optional[str] = None
    parecer_tecnico: Optional[str] = Field(None, min_length=5, max_length=5000)
    resultado: Optional[str] = Field(None, max_length=50)
    percent_conclusao: Optional[float] = None
