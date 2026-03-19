from __future__ import annotations

from flask import Blueprint, request
from app.services.behavior_service import BehaviorService
from app.schemas.behavior import BehaviorCreate, BehaviorUpdate
from app.utils.response import ok, error
from app.utils.validation import validate_schema

behavior_bp = Blueprint("behavior_bp", __name__, url_prefix="/v1")
_service = BehaviorService()

@behavior_bp.get("/behaviors")
def list_behaviors():
    cd_paciente = request.args.get("cd_paciente", type=int)
    if cd_paciente:
        return ok(_service.get_by_patient(cd_paciente))
    return ok(_service.get_all())

@behavior_bp.get("/behaviors/patient/<int:cd_paciente>")
def get_by_patient(cd_paciente: int):
    return ok(_service.get_by_patient(cd_paciente))

@behavior_bp.post("/behaviors")
@validate_schema(BehaviorCreate)
def create_behavior(data: BehaviorCreate):
    behavior_id = _service.create_behavior(data.dict())
    return ok({"id": behavior_id}, status_code=201)

@behavior_bp.put("/behaviors/<int:id>")
@validate_schema(BehaviorUpdate)
def update_behavior(id: int, data: BehaviorUpdate):
    _service.update_behavior(id, data.dict(exclude_unset=True))
    return ok({"id": id})

@behavior_bp.delete("/behaviors/<int:id>")
def delete_behavior(id: int):
    _service.delete_behavior(id)
    return ok({"id": id})
