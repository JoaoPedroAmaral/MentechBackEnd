from flask import Blueprint, request
from app.services.goal_service import GoalService
from app.schemas.goal import GoalCreate
from app.utils.response import ok
from app.utils.validation import validate_schema

goal_bp = Blueprint("goal_bp", __name__, url_prefix="/v1/goals")
_service = GoalService()

@goal_bp.get("/patient/<int:cd_paciente>")
def get_patient_goals(cd_paciente: int):
    return ok(_service.get_by_patient(cd_paciente))

@goal_bp.post("")
@validate_schema(GoalCreate)
def create_goal(data: GoalCreate):
    result = _service.create_goal(data.dict())
    return ok(result, status_code=201)

@goal_bp.patch("/relation/<int:cd_paciente_meta>/complete")
def complete_goal(cd_paciente_meta: int):
    _service.complete_goal(cd_paciente_meta)
    return ok({"message": "Meta concluída com sucesso"})

@goal_bp.patch("/<int:cd_meta>/toggle")
def toggle_goal(cd_meta: int):
    new_status = _service.toggle_goal(cd_meta)
    return ok({"id": cd_meta, "ativo": new_status})

@goal_bp.delete("/<int:cd_meta>")
def delete_goal(cd_meta: int):
    _service.remove_goal(cd_meta)
    return ok({"message": "Meta deletada"})
