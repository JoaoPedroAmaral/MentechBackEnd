from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class DisorderCreate(BaseModel):
    nm_transtorno: str
    cid11: str
    apoio_diag: Optional[str] = None
    prevalencia: Optional[str] = None
    fatores_risco_prognostico: Optional[str] = None
    diagnostico_genero: Optional[str] = None


class DisorderUpdate(BaseModel):
    nm_transtorno: Optional[str] = None
    cid11: Optional[str] = None
    apoio_diag: Optional[str] = None
    prevalencia: Optional[str] = None
    fatores_risco_prognostico: Optional[str] = None
    diagnostico_genero: Optional[str] = None


class DisorderPayloadCreate(BaseModel):
    nm_transtorno: str
    cid11: str
    apoio_diag: Optional[str] = None
    prevalencia: Optional[str] = None
    fatores_risco_prognostico: Optional[str] = None
    diagnostico_genero: Optional[str] = None


class DisorderPayloadUpdate(BaseModel):
    nm_transtorno: Optional[str] = None
    cid11: Optional[str] = None
    apoio_diag: Optional[str] = None
    prevalencia: Optional[str] = None
    fatores_risco_prognostico: Optional[str] = None
    diagnostico_genero: Optional[str] = None


class SubtypeCreate(BaseModel):
    nm_subtipo: str
    cid11: str
    obs: str


class SubtypeUpdate(BaseModel):
    nm_subtipo: Optional[str] = None
    cid11: Optional[str] = None
    obs: Optional[str] = None
    cd_transtorno: Optional[int] = None


class SeverityCreate(BaseModel):
    nm_gravidade: str
    grav_descricao: str


class SeverityUpdate(BaseModel):
    nm_gravidade: Optional[str] = None
    grav_descricao: Optional[str] = None
    cd_transtorno: Optional[int] = None


class CriterionCreate(BaseModel):
    criterio_diagnostico: str
    criterio_diferencial: Optional[str] = 'N'


class CriterionUpdate(BaseModel):
    criterio_diagnostico: Optional[str] = None
    criterio_diferencial: Optional[str] = 'N'
    cd_transtorno: Optional[int] = None


class DisorderAggregateCreate(BaseModel):
    disorder: DisorderPayloadCreate
    subtypes: list[SubtypeCreate] = []
    severities: list[SeverityCreate] = []
    criteria: list[CriterionCreate] = []


class DisorderAggregateUpdate(BaseModel):
    disorder: Optional[DisorderPayloadUpdate] = None
    subtypes: Optional[list[SubtypeCreate]] = None
    severities: Optional[list[SeverityCreate]] = None
    criteria: Optional[list[CriterionCreate]] = None
