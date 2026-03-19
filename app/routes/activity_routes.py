from flask import Blueprint, request
from app.services.activity_service import ActivityService
from app.schemas.activity import ActivityCreate, ActivityUpdate
from app.utils.response import ok
from app.utils.validation import validate_schema

activity_bp = Blueprint("activity_bp", __name__, url_prefix="/v1/activities")
_service = ActivityService()

@activity_bp.get("")
def list_activities():
    cd_paciente = request.args.get("cd_paciente", type=int)
    cd_usuario = request.args.get("cd_usuario", type=int)
    cd_meta = request.args.get("cd_meta", type=int)
    return ok(_service.get_filtered(cd_paciente, cd_usuario, cd_meta))

@activity_bp.post("")
@validate_schema(ActivityCreate)
def create_activity(data: ActivityCreate):
    activity_id = _service.create_activity(data.dict())
    return ok({"id": activity_id}, status_code=201)

@activity_bp.put("/<int:cd_atividade>")
@validate_schema(ActivityUpdate)
def update_activity(cd_atividade: int, data: ActivityUpdate):
    _service.update_activity(cd_atividade, data.dict(exclude_unset=True))
    return ok({"id": cd_atividade})

@activity_bp.patch("/<int:cd_atividade>/toggle")
def toggle_activity(cd_atividade: int):
    status = _service.toggle_active(cd_atividade)
    return ok({"id": cd_atividade, "ativo": status})

@activity_bp.delete("/<int:cd_atividade>")
def delete_activity(cd_atividade: int):
    _service.delete_activity(cd_atividade)
    return ok({"message": "Atividade deletada"})

@activity_bp.get("/<int:cd_atividade>/history")
def get_activity_history(cd_atividade: int):
    return ok(_service.get_history(cd_atividade=cd_atividade))

@activity_bp.get("/goal/<int:cd_meta>/history")
def get_goal_activity_history(cd_meta: int):
    return ok(_service.get_history(cd_meta=cd_meta))
