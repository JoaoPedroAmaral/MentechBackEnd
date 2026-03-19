from __future__ import annotations

from flask import Blueprint
from app.services.responsible_service import ResponsibleService
from app.schemas.responsible import ResponsibleCreate, ResponsibleUpdate
from app.utils.response import ok, error
from app.utils.validation import validate_schema

responsible_bp = Blueprint("responsible_bp", __name__, url_prefix="/v1")
_service = ResponsibleService()


@responsible_bp.get("/patients/<int:cd_paciente>/responsaveis")
def list_responsaveis(cd_paciente: int):
    return ok(_service.list_by_patient(cd_paciente))


@responsible_bp.post("/patients/<int:cd_paciente>/responsaveis")
@validate_schema(ResponsibleCreate)
def add_responsavel(cd_paciente: int, data: ResponsibleCreate):
    resp_id = _service.add(cd_paciente, data.dict())
    return ok({"id": resp_id}, status_code=201)


@responsible_bp.put("/patients/<int:cd_paciente>/responsaveis/<int:cd_responsavel>")
@validate_schema(ResponsibleUpdate)
def update_responsavel(cd_paciente: int, cd_responsavel: int, data: ResponsibleUpdate):
    _service.update(cd_paciente, cd_responsavel, data.dict(exclude_unset=True))
    return ok({"id": cd_responsavel})


@responsible_bp.delete("/patients/<int:cd_paciente>/responsaveis/<int:cd_responsavel>")
def delete_responsavel(cd_paciente: int, cd_responsavel: int):
    _service.remove(cd_paciente, cd_responsavel)
    return ok({"id": cd_responsavel})
