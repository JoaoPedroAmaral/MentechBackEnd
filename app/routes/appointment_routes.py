from __future__ import annotations

from flask import Blueprint, request
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.utils.response import ok, error
from app.utils.validation import validate_schema

appointment_bp = Blueprint("appointment_bp", __name__, url_prefix="/v1")
_service = AppointmentService()

@appointment_bp.get("/appointments")
def list_appointments():
    cd_usuario = request.args.get("cd_usuario", type=int)
    cd_paciente = request.args.get("cd_paciente", type=int)
    return ok(_service.get_all(cd_usuario, cd_paciente))

@appointment_bp.post("/appointments")
@validate_schema(AppointmentCreate)
def create_appointment(data: AppointmentCreate):
    appointment_id = _service.create_appointments(data.dict())
    return ok({"id": appointment_id}, status_code=201)

@appointment_bp.put("/appointments/<int:id>")
@validate_schema(AppointmentUpdate)
def update_appointment(id: int, data: AppointmentUpdate):
    _service.update_appointment(id, data.dict(exclude_unset=True))
    return ok({"id": id})

@appointment_bp.delete("/appointments/<int:id>")
def delete_appointment(id: int):
    _service.delete_appointment(id)
    return ok({"id": id})

@appointment_bp.post("/appointments/<int:id>/attendance")
def post_attendance(id: int):
    _service.mark_attendance(id)
    return ok({"id": id, "status": "Compareceu"})
