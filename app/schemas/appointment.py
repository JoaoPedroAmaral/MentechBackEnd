from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field
from datetime import date, time

class AppointmentBase(BaseModel):
    cd_usuario: int
    cd_paciente: int
    dt_agendamento: date
    hora_inicio: time
    hora_fim: time

class AppointmentCreate(AppointmentBase):
    prazo: Optional[str] = Field(None, description="Scheduling period: 1_mes, 6_meses, 1_ano")

class AppointmentUpdate(BaseModel):
    dt_agendamento: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fim: Optional[time] = None
    cd_usuario: Optional[int] = None
    cd_paciente: Optional[int] = None

class AppointmentResponse(AppointmentBase):
    cd_agendamento: int
    comparecimento: str = "N"

    model_config = {"from_attributes": True}
