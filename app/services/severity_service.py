from __future__ import annotations

from typing import Any, Dict, Optional

from app.repositories.severity_repository import SeverityRepository
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.text import normalize_and_capitalize


class SeverityService:
    _limits = {"nm_gravidade": 255, "grav_descricao": 200}

    def __init__(self, repo: Optional[SeverityRepository] = None) -> None:
        self._repo = repo or SeverityRepository()

    def get_all(self) -> list[Dict[str, Any]]:
        return self._repo.get_all()

    def get_by_transtorno(self, transtorno_id: int) -> list[Dict[str, Any]]:
        return self._repo.get_by_transtorno(transtorno_id)

    def get_by_id(self, severity_id: int) -> Dict[str, Any]:
        severity = self._repo.get_by_id(severity_id)
        if not severity:
            raise NotFoundError(message="Severity not found")
        return severity

    def create(self, nm_gravidade: str, grav_descricao: str, cd_transtorno: int) -> int:
        nm_gravidade = normalize_and_capitalize(nm_gravidade)
        grav_descricao = normalize_and_capitalize(grav_descricao)

        if not nm_gravidade or not grav_descricao or not cd_transtorno:
            raise ValidationError(message="Missing required fields", details={"legacy_code": "MSG200"})
        self._validate_length("nm_gravidade", nm_gravidade)
        self._validate_length("grav_descricao", grav_descricao)

        if self._repo.exists_duplicate(nm_gravidade, grav_descricao, cd_transtorno):
            raise ConflictError(message="Duplicate severity", details={"legacy_code": "MSG201"})

        return self._repo.create(nm_gravidade, grav_descricao, cd_transtorno)

    def update(
        self,
        severity_id: int,
        nm_gravidade: Optional[str],
        grav_descricao: Optional[str],
        cd_transtorno: Optional[int],
    ) -> None:
        if not any([nm_gravidade, grav_descricao, cd_transtorno]):
            raise ValidationError(message="No fields to update", details={"legacy_code": "MSG204"})

        existing = self._repo.get_by_id(severity_id)
        if not existing:
            raise NotFoundError(message="Severity not found")

        nm_gravidade = normalize_and_capitalize(nm_gravidade or existing["nm_gravidade"])
        grav_descricao = normalize_and_capitalize(grav_descricao or existing["grav_descricao"])
        cd_transtorno = cd_transtorno or existing["cd_transtorno"]

        self._validate_length("nm_gravidade", nm_gravidade)
        self._validate_length("grav_descricao", grav_descricao)

        if self._repo.exists_duplicate(nm_gravidade, grav_descricao, cd_transtorno, exclude_id=severity_id):
            raise ConflictError(message="Duplicate severity", details={"legacy_code": "MSG201"})

        self._repo.update(severity_id, nm_gravidade, grav_descricao, cd_transtorno)

    def delete(self, severity_id: int) -> None:
        if not self._repo.get_by_id(severity_id):
            raise NotFoundError(message="Severity not found")
        self._repo.delete(severity_id)

    def delete_by_transtorno(self, transtorno_id: int) -> None:
        self._repo.delete_by_transtorno(transtorno_id)

    def _validate_length(self, field: str, value: Optional[str]) -> None:
        if value is None:
            return
        limit = self._limits.get(field)
        if limit and (len(value) < 3 or len(value) > limit):
            raise ValidationError(message="Invalid field length", details={"legacy_code": "MSG199"})
