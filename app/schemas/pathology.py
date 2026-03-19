from pydantic import BaseModel, Field
from typing import Optional

class PathologyCreate(BaseModel):
    cd_paciente: int
    doenca: str = Field(..., max_length=150)
    obs_doenca: Optional[str] = None
    cid11: str = Field(..., max_length=20)

class PathologyUpdate(BaseModel):
    doenca: Optional[str] = Field(None, max_length=150)
    obs_doenca: Optional[str] = None
    cid11: Optional[str] = Field(None, max_length=20)
