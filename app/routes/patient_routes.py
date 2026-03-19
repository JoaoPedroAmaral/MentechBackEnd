from __future__ import annotations

from flask import Blueprint, request
from app.services.patient_service import PatientService
from app.schemas.patient import PatientCreate, PatientUpdate
from app.utils.response import ok, error
from app.utils.validation import validate_schema

patient_bp = Blueprint("patient_bp", __name__, url_prefix="/v1")
_service = PatientService()

@patient_bp.get("/patients")
def list_patients():
    cd_usuario = request.args.get("cd_usuario", type=int)
    return ok(_service.get_all(cd_usuario))

@patient_bp.get("/patients/<int:cd_paciente>")
def get_patient_details(cd_paciente: int):
    return ok(_service.get_details(cd_paciente))

@patient_bp.post("/patients")
@validate_schema(PatientCreate)
def create_patient(data: PatientCreate):
    patient_id = _service.create_full_patient(data.dict())
    return ok({"id": patient_id}, status_code=201)

@patient_bp.put("/patients/<int:cd_paciente>")
@validate_schema(PatientUpdate)
def update_patient(cd_paciente: int, data: PatientUpdate):
    _service.update_patient(cd_paciente, data.dict(exclude_unset=True))
    return ok({"id": cd_paciente})

@patient_bp.patch("/patients/<int:cd_paciente>/toggle")
def toggle_status(cd_paciente: int):
    new_status = _service.toggle_active(cd_paciente)
    return ok({"id": cd_paciente, "ativo": new_status})
