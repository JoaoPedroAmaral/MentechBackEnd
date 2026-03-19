from __future__ import annotations

from typing import Any, Dict, Optional

from app.repositories.subtype_repository import SubtypeRepository
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.text import normalize_and_capitalize, normalize_text


class SubtypeService:
    _limits = {"nm_subtipo": 500, "obs": 2000}

    def __init__(self, repo: Optional[SubtypeRepository] = None) -> None:
        self._repo = repo or SubtypeRepository()

    def get_all(self) -> list[Dict[str, Any]]:
        return self._repo.get_all()

    def get_by_transtorno(self, transtorno_id: int) -> list[Dict[str, Any]]:
        return self._repo.get_by_transtorno(transtorno_id)

    def get_by_id(self, subtype_id: int) -> Dict[str, Any]:
        subtype = self._repo.get_by_id(subtype_id)
        if not subtype:
            raise NotFoundError(message="Subtype not found")
        return subtype

    def create(self, nm_subtipo: str, cid11: str, obs: str, cd_transtorno: int) -> int:
        nm_subtipo = normalize_and_capitalize(nm_subtipo)
        cid11 = normalize_text(cid11)
        obs = normalize_and_capitalize(obs)

        if not nm_subtipo or not cid11 or not obs or not cd_transtorno:
            raise ValidationError(message="Missing required fields", details={"legacy_code": "MSG200"})
        self._validate_length("nm_subtipo", nm_subtipo)
        self._validate_length("obs", obs)

        if self._repo.exists_duplicate(nm_subtipo, cid11):
            raise ConflictError(message="Duplicate subtype", details={"legacy_code": "MSG201"})

        return self._repo.create(nm_subtipo, cid11, obs, cd_transtorno)

    def update(
        self,
        subtype_id: int,
        nm_subtipo: Optional[str],
        cid11: Optional[str],
        obs: Optional[str],
        cd_transtorno: Optional[int],
    ) -> None:
        if not any([nm_subtipo, cid11, obs, cd_transtorno]):
            raise ValidationError(message="No fields to update", details={"legacy_code": "MSG204"})

        existing = self._repo.get_by_id(subtype_id)
        if not existing:
            raise NotFoundError(message="Subtype not found")

        nm_subtipo = normalize_and_capitalize(nm_subtipo or existing["nm_subtipo"])
        cid11 = normalize_text(cid11 or existing["cid11"])
        obs = normalize_and_capitalize(obs or existing["obs"])
        cd_transtorno = cd_transtorno or existing["cd_transtorno"]

        self._validate_length("nm_subtipo", nm_subtipo)
        self._validate_length("obs", obs)

        if self._repo.exists_duplicate(nm_subtipo, cid11, cd_transtorno, exclude_id=subtype_id):
            raise ConflictError(message="Duplicate subtype", details={"legacy_code": "MSG202"})

        self._repo.update(subtype_id, existing["cd_cid"], nm_subtipo, cid11, obs, cd_transtorno)

    def delete(self, subtype_id: int) -> None:
        if not self._repo.get_by_id(subtype_id):
            raise NotFoundError(message="Subtype not found")
        self._repo.delete(subtype_id)

    def delete_by_transtorno(self, transtorno_id: int) -> None:
        self._repo.delete_by_transtorno(transtorno_id)

    def _validate_length(self, field: str, value: Optional[str]) -> None:
        if value is None:
            return
        limit = self._limits.get(field)
        if limit and (len(value) < 4 or len(value) > limit):
            raise ValidationError(message="Invalid field length", details={"legacy_code": "MSG199"})
