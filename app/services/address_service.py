from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.repositories.address_repository import AddressRepository
from app.repositories.patient_repository import PatientRepository
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.cache import TTLCache
from app.config import Config


class AddressService:
    def __init__(
        self,
        address_repo: Optional[AddressRepository] = None,
        patient_repo: Optional[PatientRepository] = None,
    ) -> None:
        self._address_repo = address_repo or AddressRepository()
        self._patient_repo = patient_repo or PatientRepository()
        self._cache = TTLCache(Config.CACHE_TTL_SECONDS)

    def _assert_patient_exists(self, cd_paciente: int) -> None:
        if not self._patient_repo.get_by_id(cd_paciente):
            raise NotFoundError("Patient not found")

    def _assert_address_belongs(self, cd_endereco: int, cd_paciente: int) -> Dict[str, Any]:
        addr = self._address_repo.get_by_id(cd_endereco)
        if not addr:
            raise NotFoundError("Address not found")
        if addr["cd_paciente"] != cd_paciente:
            raise ValidationError("Address does not belong to this patient")
        return addr

    def _invalidate(self, cd_paciente: int) -> None:
        self._cache.invalidate(f"patient:details:{cd_paciente}")
        self._cache.invalidate("patients:all")

    def list_by_patient(self, cd_paciente: int) -> List[Dict[str, Any]]:
        self._assert_patient_exists(cd_paciente)
        return self._address_repo.get_by_patient_id(cd_paciente)

    def add(self, cd_paciente: int, data: Dict[str, Any]) -> int:
        self._assert_patient_exists(cd_paciente)
        addr_id = self._address_repo.create({
            "cd_paciente": cd_paciente,
            "tipo": data.get("tipo", "PACIENTE").upper(),
            "cep": data["cep"],
            "cidade": data["cidade"],
            "bairro": data["bairro"],
            "logradouro": data["logradouro"],
            "uf": data["uf"].upper(),
            "numero": data["numero"],
            "complemento": data.get("complemento"),
            "cd_responsavel": data.get("cd_responsavel"),
        })
        self._invalidate(cd_paciente)
        return addr_id

    def update(self, cd_paciente: int, cd_endereco: int, data: Dict[str, Any]) -> None:
        self._assert_address_belongs(cd_endereco, cd_paciente)
        payload: Dict[str, Any] = {}
        for field in ["cep", "cidade", "bairro", "logradouro", "numero", "complemento", "cd_responsavel"]:
            if field in data:
                payload[field] = data[field]
        if "tipo" in data:
            payload["tipo"] = data["tipo"].upper()
        if "uf" in data:
            payload["uf"] = data["uf"].upper()
        if payload:
            self._address_repo.update(cd_endereco, payload)
            self._invalidate(cd_paciente)

    def remove(self, cd_paciente: int, cd_endereco: int) -> None:
        self._assert_address_belongs(cd_endereco, cd_paciente)
        self._address_repo.delete(cd_endereco)
        self._invalidate(cd_paciente)
