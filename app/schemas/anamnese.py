from __future__ import annotations

from typing import List, Optional, Any
from pydantic import BaseModel

class AnamneseResponseSave(BaseModel):
    cd_questao: int
    cd_anamnese: int
    cd_alternativa: Optional[List[int]] = None
    txt_resposta: Optional[str] = None

class AnamneseGenerateRequest(BaseModel):
    cd_perfil: int
    cd_paciente: int

class AnamneseQuestion(BaseModel):
    cd_questao: int
    txt_questao: str
    cd_tipo_questao: int
    obrigatorio: str
    tipo_questao: str
    cd_perfil: int
    perfil_questao: str

class AnamneseFullResponse(BaseModel):
    cd_anamnese: int
    cd_paciente: int
    nm_paciente: str
    questoes: List[dict]
