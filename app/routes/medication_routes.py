from __future__ import annotations

from flask import Blueprint, request
from app.services.medication_service import MedicationService
from app.schemas.medication import MedicationCreate, MedicationUpdate, PrescriptionCreate, PrescriptionUpdate
from app.utils.response import ok
from app.utils.validation import validate_schema
from app.services.log_service import LogService

medication_bp = Blueprint("medication_bp", __name__, url_prefix="/v1")
_service = MedicationService()

@medication_bp.get("/medications")
def list_medications():
    cd_paciente = request.args.get("cd_paciente", type=int)
    if cd_paciente:
        return ok(_service.get_by_patient(cd_paciente))
    return ok(_service.get_all())

@medication_bp.get("/medications/patient/<int:cd_paciente>")
def get_by_patient(cd_paciente: int):
    return ok(_service.get_by_patient(cd_paciente))

@medication_bp.post("/medications")
@validate_schema(MedicationCreate)
def create_medication(data: MedicationCreate):
    med_id = _service.create_medication(data.dict())
    return ok({"id": med_id}, status_code=201)

@medication_bp.put("/medications/<int:id>")
@validate_schema(MedicationUpdate)
def update_medication(id: int, data: MedicationUpdate):
    _service.update_medication(id, data.dict(exclude_unset=True))
    return ok({"id": id})

@medication_bp.delete("/medications/<int:id>")
def delete_medication(id: int):
    _service.delete_medication(id)
    return ok({"id": id})

@medication_bp.post("/medications/prescribe")
@validate_schema(PrescriptionCreate)
def prescribe_medication(data: PrescriptionCreate):
    pm_id = _service.prescribe(data.dict())
    LogService().register_action("PMD", cd_paciente=data.cd_paciente, adicional="Medicamento prescrito ao paciente")
    return ok({"id": pm_id}, status_code=201)

@medication_bp.put("/medications/prescriptions/<int:id>")
@validate_schema(PrescriptionUpdate)
def update_prescription(id: int, data: PrescriptionUpdate):
    cd_paciente = request.args.get("cd_paciente", type=int) or 0
    _service.update_prescription(id, cd_paciente, data.dict(exclude_unset=True))
    LogService().register_action("AMPD", cd_paciente=cd_paciente, adicional=f"Prescrição {id} atualizada")
    return ok({"id": id})

@medication_bp.delete("/medications/prescriptions/<int:id>")
def delete_prescription(id: int):
    cd_paciente = request.args.get("cd_paciente", type=int) or 0
    _service.delete_prescription(id, cd_paciente)
    return ok({"message": "Prescrição removida"})
