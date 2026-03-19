from __future__ import annotations
from flask import Blueprint, request
from app.services.medical_record_service import MedicalRecordService
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate
from app.utils.response import ok, error
from app.utils.validation import validate_schema

medical_record_bp = Blueprint("medical_record_bp", __name__, url_prefix="/v1/medical-records")
_service = MedicalRecordService()

@medical_record_bp.get("")
def list_records():
    cd_paciente = request.args.get("cd_paciente", type=int)
    return ok(_service.get_all(cd_paciente))

@medical_record_bp.post("")
@validate_schema(MedicalRecordCreate)
def create_record(data: MedicalRecordCreate):
    record_id = _service.create(data.dict())
    return ok({"id": record_id}, status_code=201)

@medical_record_bp.put("/<int:cd_prontuario>")
@validate_schema(MedicalRecordUpdate)
def update_record(cd_prontuario: int, data: MedicalRecordUpdate):
    _service.update(cd_prontuario, data.dict(exclude_unset=True))
    return ok({"id": cd_prontuario})

@medical_record_bp.delete("/<int:cd_prontuario>")
def delete_record(cd_prontuario: int):
    _service.delete(cd_prontuario)
    return ok({"message": "Medical record removed"})
