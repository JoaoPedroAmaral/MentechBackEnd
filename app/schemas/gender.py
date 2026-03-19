from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

class GenderBase(BaseModel):
    nm_genero: str

class GenderCreate(GenderBase):
    pass

class GenderUpdate(GenderBase):
    pass

class GenderResponse(GenderBase):
    cd_genero: int
