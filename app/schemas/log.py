from pydantic import BaseModel, Field
from typing import Optional

class LogCreate(BaseModel):
    cd_usuario: int
    tipo_log: str = Field(..., max_length=10)
    mensagem_adicional: Optional[str] = None
    cd_paciente: Optional[int] = None
    cd_transtorno: Optional[int] = None
    cd_meta: Optional[int] = None
