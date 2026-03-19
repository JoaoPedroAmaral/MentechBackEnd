from app.repositories.patient_medication_repository import PatientMedicationRepository
from app.utils.text import normalize_and_capitalize

class PatientMedicationService:
    def __init__(self):
        self._repo = PatientMedicationRepository()

    def get_all(self):
        return self._repo.get_all()

    def create_prescription(self, data: dict):
        data["dose"] = normalize_and_capitalize(data["dose"])
        return self._repo.create(data)

    def update_prescription(self, id: int, data: dict):
        if "dose" in data:
            data["dose"] = normalize_and_capitalize(data["dose"])
        self._repo.update(id, data)

    def delete_prescription(self, id: int):
        self._repo.delete(id)
