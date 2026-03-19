from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

class BehaviorBase(BaseModel):
    comportamento_paciente: str = Field(..., min_length=5, max_length=2000)
    cd_paciente: int

class BehaviorCreate(BehaviorBase):
    pass

class BehaviorUpdate(BaseModel):
    comportamento_paciente: Optional[str] = Field(None, min_length=5, max_length=2000)
    cd_paciente: Optional[int] = None

class BehaviorResponse(BehaviorBase):
    cd_comportamento_paciente: int

    model_config = {"from_attributes": True}
