from __future__ import annotations

from typing import Any, Dict, Optional

from app.repositories.criteria_repository import CriteriaRepository
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.text import normalize_and_capitalize


class CriteriaService:
    _limits = {"criterio_diagnostico": 2000}
    _allowed_diferencial = {0, 1}

    def __init__(self, repo: Optional[CriteriaRepository] = None) -> None:
        self._repo = repo or CriteriaRepository()

    def get_all(self) -> list[Dict[str, Any]]:
        return self._repo.get_all()

    def get_by_transtorno(self, transtorno_id: int) -> list[Dict[str, Any]]:
        return self._repo.get_by_transtorno(transtorno_id)

    def get_by_id(self, criterio_id: int) -> Dict[str, Any]:
        criterio = self._repo.get_by_id(criterio_id)
        if not criterio:
            raise NotFoundError(message="Criterion not found")
        return criterio

    def create(self, criterio_diagnostico: str, criterio_diferencial: Optional[str], cd_transtorno: int) -> int:
        criterio_diagnostico = normalize_and_capitalize(criterio_diagnostico)
        criterio_diferencial = self._normalize_diferencial(criterio_diferencial)

        if not criterio_diagnostico or not cd_transtorno:
            raise ValidationError(message="Missing required fields", details={"legacy_code": "MSG200"})
        self._validate_length("criterio_diagnostico", criterio_diagnostico)

        if self._repo.exists_duplicate(criterio_diagnostico, criterio_diferencial, cd_transtorno):
            raise ConflictError(message="Duplicate criterion", details={"legacy_code": "MSG211"})

        return self._repo.create(criterio_diagnostico, criterio_diferencial, cd_transtorno)

    def update(
        self,
        criterio_id: int,
        criterio_diagnostico: Optional[str],
        criterio_diferencial: Optional[str],
        cd_transtorno: Optional[int],
    ) -> None:
        if criterio_diagnostico is None and criterio_diferencial is None and cd_transtorno is None:
            raise ValidationError(message="No fields to update", details={"legacy_code": "MSG204"})

        existing = self._repo.get_by_id(criterio_id)
        if not existing:
            raise NotFoundError(message="Criterion not found")

        criterio_diagnostico = normalize_and_capitalize(criterio_diagnostico or existing["criterio_diagnostico"])
        criterio_diferencial = (
            criterio_diferencial if criterio_diferencial is not None else existing["criterio_diferencial"]
        )
        criterio_diferencial = self._normalize_diferencial(criterio_diferencial)
        cd_transtorno = cd_transtorno or existing["cd_transtorno"]

        if not criterio_diagnostico:
            raise ValidationError(message="Missing required fields", details={"legacy_code": "MSG200"})
        self._validate_length("criterio_diagnostico", criterio_diagnostico)

        if self._repo.exists_duplicate(criterio_diagnostico, criterio_diferencial, cd_transtorno, exclude_id=criterio_id):
            raise ConflictError(message="Duplicate criterion", details={"legacy_code": "MSG211"})

        self._repo.update(criterio_id, criterio_diagnostico, criterio_diferencial, cd_transtorno)

    def delete(self, criterio_id: int) -> None:
        if not self._repo.get_by_id(criterio_id):
            raise NotFoundError(message="Criterion not found")
        self._repo.delete(criterio_id)

    def delete_by_transtorno(self, transtorno_id: int) -> None:
        self._repo.delete_by_transtorno(transtorno_id)

    def _normalize_diferencial(self, value: Optional[int]) -> int:
        if value is None:
            return 0
        if value not in self._allowed_diferencial:
            raise ValidationError(message="Invalid criterio_diferencial", details={"allowed": [0, 1]})
        return int(value)

    def _validate_length(self, field: str, value: Optional[str]) -> None:
        if value is None:
            return
        limit = self._limits.get(field)
        if limit and (len(value) < 3 or len(value) > limit):
            raise ValidationError(message="Invalid field length", details={"legacy_code": "MSG199"})
