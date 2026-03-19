from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.repositories.medication_repository import MedicationRepository
from app.utils.text import normalize_and_capitalize
from app.utils.exceptions import ValidationError, NotFoundError
from app.utils.cache import TTLCache

class MedicationService:
    def __init__(self, repository: Optional[MedicationRepository] = None) -> None:
        self._repo = repository or MedicationRepository()
        self._cache = TTLCache(600)

    def get_all(self) -> List[Dict[str, Any]]:
        return self._repo.get_all()

    def get_by_patient(self, cd_paciente: int) -> List[Dict[str, Any]]:
        cache_key = f"medication:patient:{cd_paciente}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached
            
        meds = self._repo.get_by_patient(cd_paciente)
        self._cache.set(cache_key, meds)
        return meds

    def create_medication(self, data: Dict[str, Any]) -> int:
        nm_medicamento = normalize_and_capitalize(data['nm_medicamento'])
        dosagem = data['dosagem']

        if self._repo.check_exists(nm_medicamento, dosagem):
            raise ValidationError("Medication with this dosage already exists", code="MSG211")

        data['nm_medicamento'] = nm_medicamento
        if 'forma_farmaceutica' in data and data['forma_farmaceutica']:
            data['forma_farmaceutica'] = normalize_and_capitalize(data['forma_farmaceutica'])
        if 'principio_ativo' in data and data['principio_ativo']:
            data['principio_ativo'] = normalize_and_capitalize(data['principio_ativo'])
        if 'fabricante' in data and data['fabricante']:
            data['fabricante'] = normalize_and_capitalize(data['fabricante'])

        med_id = self._repo.create(data)
        return med_id

    def update_medication(self, cd_medicamento: int, data: Dict[str, Any]) -> None:
        if not self._repo.get_by_id(cd_medicamento):
            raise NotFoundError("Medication not found")

        for field in ['nm_medicamento', 'forma_farmaceutica', 'principio_ativo', 'fabricante']:
            if field in data and data[field]:
                data[field] = normalize_and_capitalize(data[field])

        self._repo.update(cd_medicamento, data)
        self._cache.invalidate_all()

    def delete_medication(self, cd_medicamento: int) -> None:
        if not self._repo.get_by_id(cd_medicamento):
            raise NotFoundError("Medication not found")
        self._repo.delete(cd_medicamento)
        self._cache.invalidate_all()

    def prescribe(self, data: Dict[str, Any]) -> int:
        data["dose"] = normalize_and_capitalize(data["dose"])
        pm_id = self._repo.prescribe_to_patient(data)
        self._cache.invalidate(f"medication:patient:{data['cd_paciente']}")
        return pm_id

    def update_prescription(self, pm_id: int, cd_paciente: int, data: Dict[str, Any]) -> None:
        if "dose" in data:
            data["dose"] = normalize_and_capitalize(data["dose"])
        self._repo.update_prescription(pm_id, data)
        self._cache.invalidate(f"medication:patient:{cd_paciente}")

    def delete_prescription(self, pm_id: int, cd_paciente: int) -> None:
        self._repo.delete_prescription(pm_id)
        self._cache.invalidate(f"medication:patient:{cd_paciente}")
