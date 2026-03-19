from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.repositories.medical_record_repository import MedicalRecordRepository
from app.utils.text import normalize_and_capitalize, format_date_to_db

class MedicalRecordService:
    def __init__(self, repo: Optional[MedicalRecordRepository] = None) -> None:
        self._repo = repo or MedicalRecordRepository()

    def get_all(self, cd_paciente: Optional[int] = None) -> List[Dict[str, Any]]:
        if cd_paciente:
            return self._repo.get_by_patient(cd_paciente)
        return self._repo.get_all()

    def create(self, data: Dict[str, Any]) -> int:
        data['txt_prontuario'] = data['txt_prontuario'].strip().capitalize()
        data['dt_prontuario'] = format_date_to_db(data['dt_prontuario'])
        return self._repo.create(data)

    def update(self, cd_prontuario: int, data: Dict[str, Any]) -> None:
        if 'txt_prontuario' in data:
            data['txt_prontuario'] = data['txt_prontuario'].strip().capitalize()
        if 'dt_prontuario' in data:
            data['dt_prontuario'] = format_date_to_db(data['dt_prontuario'])
        
        self._repo.update(cd_prontuario, data)

    def delete(self, cd_prontuario: int) -> None:
        self._repo.delete(cd_prontuario)
