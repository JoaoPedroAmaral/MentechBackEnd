from typing import Optional
from pydantic import BaseModel, Field

class GoalCreate(BaseModel):
    meta: str = Field(..., min_length=3, max_length=100)
    obs_meta: str = Field(..., min_length=3, max_length=500)
    cd_paciente: int
    dt_previsao: str

class GoalUpdate(BaseModel):
    meta: Optional[str] = Field(None, min_length=3, max_length=100)
    obs_meta: Optional[str] = Field(None, min_length=3, max_length=500)
