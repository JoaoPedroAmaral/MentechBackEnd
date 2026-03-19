from flask import Blueprint, request
from app.services.patient_medication_service import PatientMedicationService
from app.schemas.patient_medication import PatientMedicationCreate, PatientMedicationUpdate
from app.utils.response import ok
from app.utils.validation import validate_schema
from app.services.log_service import LogService

patient_medication_bp = Blueprint("patient_medication_bp", __name__, url_prefix="/v1/patient-medications")
_service = PatientMedicationService()

@patient_medication_bp.get("")
def get_patient_medications():
    return ok(_service.get_all())

@patient_medication_bp.post("")
@validate_schema(PatientMedicationCreate)
def create_patient_medication(data: PatientMedicationCreate):
    pm_id = _service.create_prescription(data.dict())
    LogService().register_action("PMD", cd_paciente=data.cd_paciente, adicional="Prescrição vinculada")
    return ok({"id": pm_id}, status_code=201)

@patient_medication_bp.put("/<int:id>")
@validate_schema(PatientMedicationUpdate)
def update_patient_medication(id: int, data: PatientMedicationUpdate):
    _service.update_prescription(id, data.dict(exclude_unset=True))
    LogService().register_action("AMPD", adicional=f"Prescrição atualizada no ID {id}")
    return ok({"id": id})

@patient_medication_bp.delete("/<int:id>")
def delete_patient_medication(id: int):
    _service.delete_prescription(id)
    return ok({"message": "Prescrição desvinculada"})
