from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.repositories.responsible_repository import ResponsibleRepository
from app.repositories.patient_repository import PatientRepository
from app.utils.text import normalize_and_capitalize, format_date_to_db
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.cache import TTLCache
from app.config import Config


class ResponsibleService:
    def __init__(
        self,
        resp_repo: Optional[ResponsibleRepository] = None,
        patient_repo: Optional[PatientRepository] = None,
    ) -> None:
        self._resp_repo = resp_repo or ResponsibleRepository()
        self._patient_repo = patient_repo or PatientRepository()
        self._cache = TTLCache(Config.CACHE_TTL_SECONDS)

    def _assert_patient_exists(self, cd_paciente: int) -> None:
        if not self._patient_repo.get_by_id(cd_paciente):
            raise NotFoundError("Patient not found")

    def _assert_responsible_belongs(self, cd_responsavel: int, cd_paciente: int) -> Dict[str, Any]:
        resp = self._resp_repo.get_by_id(cd_responsavel)
        if not resp:
            raise NotFoundError("Responsible not found")
        if resp["cd_paciente"] != cd_paciente:
            raise ValidationError("Responsible does not belong to this patient")
        return resp

    def _invalidate(self, cd_paciente: int) -> None:
        self._cache.invalidate(f"patient:details:{cd_paciente}")
        self._cache.invalidate("patients:all")

    def list_by_patient(self, cd_paciente: int) -> List[Dict[str, Any]]:
        self._assert_patient_exists(cd_paciente)
        return self._resp_repo.get_by_patient_id(cd_paciente)

    def add(self, cd_paciente: int, data: Dict[str, Any]) -> int:
        self._assert_patient_exists(cd_paciente)
        resp_id = self._resp_repo.create({
            "cd_paciente": cd_paciente,
            "cpf": data["cpf"],
            "nome": normalize_and_capitalize(data["nome"]),
            "dt_nascimento": format_date_to_db(data["dt_nascimento"]),
        })
        self._invalidate(cd_paciente)
        return resp_id

    def update(self, cd_paciente: int, cd_responsavel: int, data: Dict[str, Any]) -> None:
        self._assert_responsible_belongs(cd_responsavel, cd_paciente)
        payload: Dict[str, Any] = {}
        if "cpf" in data:
            payload["cpf"] = data["cpf"]
        if "nome" in data:
            payload["nome"] = normalize_and_capitalize(data["nome"])
        if "dt_nascimento" in data:
            payload["dt_nascimento"] = format_date_to_db(data["dt_nascimento"])
        if payload:
            self._resp_repo.update(cd_responsavel, payload)
            self._invalidate(cd_paciente)

    def remove(self, cd_paciente: int, cd_responsavel: int) -> None:
        self._assert_responsible_belongs(cd_responsavel, cd_paciente)
        self._resp_repo.delete(cd_responsavel)
        self._invalidate(cd_paciente)
