from __future__ import annotations
from flask import Blueprint, request
from app.services.patient_disorder_service import PatientDisorderService
from app.schemas.patient_disorder import PatientDisorderLink, PatientDisorderUpdate
from app.utils.response import ok, error
from app.utils.validation import validate_schema

patient_disorder_bp = Blueprint("patient_disorder_bp", __name__, url_prefix="/v1/patient-disorders")
_service = PatientDisorderService()

@patient_disorder_bp.get("/patient/<int:cd_paciente>")
def list_by_patient(cd_paciente: int):
    return ok(_service.get_by_patient(cd_paciente))

@patient_disorder_bp.post("")
@validate_schema(PatientDisorderLink)
def link_disorder(data: PatientDisorderLink):
    _service.link(data.cd_paciente, data.cd_transtorno, data.datas)
    return ok({"message": "Disorder linked to patient"}, status_code=201)

@patient_disorder_bp.put("/patient/<int:cd_paciente>/disorder/<int:cd_transtorno>")
@validate_schema(PatientDisorderUpdate)
def update_link(cd_paciente: int, cd_transtorno: int, data: PatientDisorderUpdate):
    _service.update_link(cd_paciente, cd_transtorno, data.datas)
    return ok({"message": "Link updated"})

@patient_disorder_bp.delete("/patient/<int:cd_paciente>/disorder/<int:cd_transtorno>")
def unlink_disorder(cd_paciente: int, cd_transtorno: int):
    _service.unlink(cd_paciente, cd_transtorno)
    return ok({"message": "Disorder unlinked from patient"})
