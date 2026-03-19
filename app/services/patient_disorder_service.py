from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.repositories.patient_disorder_repository import PatientDisorderRepository
from app.utils.text import format_date_to_db

class PatientDisorderService:
    def __init__(self, repo: Optional[PatientDisorderRepository] = None) -> None:
        self._repo = repo or PatientDisorderRepository()

    def get_by_patient(self, cd_paciente: int) -> List[Dict[str, Any]]:
        return self._repo.get_by_patient(cd_paciente)

    def link(self, cd_paciente: int, cd_transtorno: int, datas: Optional[str] = None) -> None:
        data_vinculo = format_date_to_db(datas) if datas else datetime.now().strftime('%Y-%m-%d')
        self._repo.link(cd_paciente, cd_transtorno, data_vinculo)

    def update_link(self, cd_paciente: int, cd_transtorno: int, datas: str) -> None:
        data_vinculo = format_date_to_db(datas)
        self._repo.update(cd_paciente, cd_transtorno, data_vinculo)

    def unlink(self, cd_paciente: int, cd_transtorno: int) -> None:
        self._repo.unlink(cd_paciente, cd_transtorno)
