from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.config import Config
from app.repositories.disorder_repository import DisorderRepository, DuplicateError
from app.utils.cache import TTLCache
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.text import normalize_and_capitalize, normalize_text


class DisorderService:
    _limits = {
        "nm_transtorno": 100,
        "apoio_diag": 3000,
        "prevalencia": 1000,
        "fatores_risco_prognostico": 30000,
        "diagnostico_genero": 1000,
    }

    _subtype_limits = {"nm_subtipo": 500, "obs": 2000}
    _severity_limits = {"nm_gravidade": 255, "grav_descricao": 200}
    _criteria_limits = {"criterio_diagnostico": 2000}

    def __init__(self, repo: Optional[DisorderRepository] = None) -> None:
        self._repo = repo or DisorderRepository()
        self._cache = TTLCache(Config.CACHE_TTL_SECONDS)
        self._details_cache = TTLCache(Config.CACHE_TTL_SECONDS)

    def get_all(self) -> list[Dict[str, Any]]:
        cached = self._cache.get("disorders")
        if cached is not None:
            return cached
        data = self._repo.get_all()
        self._cache.set("disorders", data)
        return data

    def get_all_details(self) -> list[Dict[str, Any]]:
        cached = self._details_cache.get("disorders:details")
        if cached is not None:
            return cached
        data = self._repo.get_all_details()
        self._details_cache.set("disorders:details", data)
        return data

    def get_by_id(self, transtorno_id: int) -> Dict[str, Any]:
        disorder = self._repo.get_by_id(transtorno_id)
        if not disorder:
            raise NotFoundError(message="Disorder not found", details={"legacy_code": "MSG204"})
        return disorder

    def create(
        self,
        nm_transtorno: str,
        cid11: str,
        apoio_diag: Optional[str],
        prevalencia: Optional[str],
        fatores_risco_prognostico: Optional[str],
        diagnostico_genero: Optional[str],
    ) -> int:
        nm_transtorno = normalize_and_capitalize(nm_transtorno)
        cid11 = normalize_text(cid11)
        apoio_diag = normalize_and_capitalize(apoio_diag)
        prevalencia = normalize_and_capitalize(prevalencia)
        fatores_risco_prognostico = normalize_and_capitalize(fatores_risco_prognostico)
        diagnostico_genero = normalize_and_capitalize(diagnostico_genero)

        if not nm_transtorno or not cid11:
            raise ValidationError(message="Missing required fields", details={"legacy_code": "MSG200"})

        self._validate_length("nm_transtorno", nm_transtorno)
        self._validate_optional("apoio_diag", apoio_diag)
        self._validate_optional("prevalencia", prevalencia)
        self._validate_optional("fatores_risco_prognostico", fatores_risco_prognostico)
        self._validate_optional("diagnostico_genero", diagnostico_genero)

        if self._repo.exists_duplicate(nm_transtorno, cid11):
            raise ConflictError(message="Duplicate disorder", details={"legacy_code": "MSG201"})

        disorder_id = self._repo.create(
            nm_transtorno,
            cid11,
            apoio_diag,
            prevalencia,
            fatores_risco_prognostico,
            diagnostico_genero,
        )
        self._cache.invalidate("disorders")
        self._details_cache.invalidate("disorders:details")
        self._details_cache.invalidate(f"details:{disorder_id}")
        return disorder_id

    def create_full(
        self,
        disorder: Dict[str, Any],
        subtypes: List[Dict[str, Any]],
        severities: List[Dict[str, Any]],
        criteria: List[Dict[str, Any]],
    ) -> int:
        normalized_disorder = self._normalize_disorder_create(disorder)
        normalized_subtypes = self._normalize_subtypes(subtypes)
        normalized_severities = self._normalize_severities(severities)
        normalized_criteria = self._normalize_criteria(criteria)

        try:
            disorder_id = self._repo.create_full(
                normalized_disorder,
                normalized_subtypes,
                normalized_severities,
                normalized_criteria,
            )
        except DuplicateError as exc:
            raise ConflictError(message=str(exc), details={"code": exc.code}) from exc

        self._cache.invalidate("disorders")
        self._details_cache.invalidate("disorders:details")
        self._details_cache.invalidate(f"details:{disorder_id}")
        return disorder_id

    def update(
        self,
        transtorno_id: int,
        nm_transtorno: Optional[str],
        cid11: Optional[str],
        apoio_diag: Optional[str],
        prevalencia: Optional[str],
        fatores_risco_prognostico: Optional[str],
        diagnostico_genero: Optional[str],
    ) -> None:
        if not any([nm_transtorno, cid11, apoio_diag, prevalencia, fatores_risco_prognostico, diagnostico_genero]):
            raise ValidationError(message="No fields to update", details={"legacy_code": "MSG204"})

        existing = self._repo.get_by_id(transtorno_id)
        if not existing:
            raise NotFoundError(message="Disorder not found", details={"legacy_code": "MSG204"})

        nm_transtorno = normalize_and_capitalize(nm_transtorno or existing["nm_transtorno"])
        cid11 = normalize_text(cid11 or existing["cid11"])
        apoio_diag = normalize_and_capitalize(apoio_diag or existing.get("apoio_diag"))
        prevalencia = normalize_and_capitalize(prevalencia or existing.get("prevalencia"))
        fatores_risco_prognostico = normalize_and_capitalize(
            fatores_risco_prognostico or existing.get("fatores_risco_prognostico")
        )
        diagnostico_genero = normalize_and_capitalize(diagnostico_genero or existing.get("diagnostico_genero"))

        self._validate_length("nm_transtorno", nm_transtorno)
        self._validate_optional("apoio_diag", apoio_diag)
        self._validate_optional("prevalencia", prevalencia)
        self._validate_optional("fatores_risco_prognostico", fatores_risco_prognostico)
        self._validate_optional("diagnostico_genero", diagnostico_genero)

        if self._repo.exists_duplicate(nm_transtorno, cid11, exclude_id=transtorno_id):
            raise ConflictError(message="Duplicate disorder", details={"legacy_code": "MSG201"})

        self._repo.update(
            transtorno_id,
            existing["cd_cid"],
            nm_transtorno,
            cid11,
            apoio_diag,
            prevalencia,
            fatores_risco_prognostico,
            diagnostico_genero,
        )
        self._cache.invalidate("disorders")
        self._details_cache.invalidate("disorders:details")
        self._details_cache.invalidate(f"details:{transtorno_id}")

    def update_full(
        self,
        transtorno_id: int,
        disorder: Optional[Dict[str, Any]],
        subtypes: Optional[List[Dict[str, Any]]],
        severities: Optional[List[Dict[str, Any]]],
        criteria: Optional[List[Dict[str, Any]]],
    ) -> None:
        if disorder is None and subtypes is None and severities is None and criteria is None:
            raise ValidationError(message="No fields to update", details={"legacy_code": "MSG204"})

        existing = self._repo.get_by_id(transtorno_id)
        if not existing:
            raise NotFoundError(message="Disorder not found", details={"legacy_code": "MSG204"})

        normalized_disorder = None
        if disorder is not None:
            if not any(disorder.values()):
                normalized_disorder = None
            else:
                payload = {
                    "nm_transtorno": disorder.get("nm_transtorno") or existing["nm_transtorno"],
                    "cid11": disorder.get("cid11") or existing["cid11"],
                    "apoio_diag": disorder.get("apoio_diag", existing.get("apoio_diag")),
                    "prevalencia": disorder.get("prevalencia", existing.get("prevalencia")),
                    "fatores_risco_prognostico": disorder.get(
                        "fatores_risco_prognostico",
                        existing.get("fatores_risco_prognostico"),
                    ),
                    "diagnostico_genero": disorder.get("diagnostico_genero", existing.get("diagnostico_genero")),
                }
                normalized_disorder = self._normalize_disorder_update(payload)

        normalized_subtypes = self._normalize_subtypes(subtypes) if subtypes is not None else None
        normalized_severities = self._normalize_severities(severities) if severities is not None else None
        normalized_criteria = self._normalize_criteria(criteria) if criteria is not None else None

        try:
            self._repo.update_full(
                transtorno_id,
                normalized_disorder,
                normalized_subtypes,
                normalized_severities,
                normalized_criteria,
            )
        except DuplicateError as exc:
            raise ConflictError(message=str(exc), details={"code": exc.code}) from exc

        self._cache.invalidate("disorders")
        self._details_cache.invalidate("disorders:details")
        self._details_cache.invalidate(f"details:{transtorno_id}")

    def delete(self, transtorno_id: int) -> None:
        existing = self._repo.get_by_id(transtorno_id)
        if not existing:
            raise NotFoundError(message="Disorder not found", details={"legacy_code": "MSG204"})
        self._repo.delete_cascade(transtorno_id)
        self._cache.invalidate("disorders")
        self._details_cache.invalidate("disorders:details")
        self._details_cache.invalidate(f"details:{transtorno_id}")

    def get_details(self, transtorno_id: int) -> Dict[str, Any]:
        cache_key = f"details:{transtorno_id}"
        cached = self._details_cache.get(cache_key)
        if cached is not None:
            return cached
        details = self._repo.get_details(transtorno_id)
        if not details.get("disorder"):
            raise NotFoundError(message="Disorder not found")
        self._details_cache.set(cache_key, details)
        return details

    def _normalize_disorder_create(self, disorder: Dict[str, Any]) -> Dict[str, Any]:
        nm_transtorno = normalize_and_capitalize(disorder.get("nm_transtorno"))
        cid11 = normalize_text(disorder.get("cid11"))
        apoio_diag = normalize_and_capitalize(disorder.get("prevalencia"))
        fatores_risco_prognostico = normalize_and_capitalize(disorder.get("fatores_risco_prognostico"))
        diagnostico_genero = normalize_and_capitalize(disorder.get("apoio_diag"))
        prevalencia = normalize_and_capitalize(disorder.get("diagnostico_genero"))

        if not nm_transtorno or not cid11:
            raise ValidationError(message="Missing required fields", details={"legacy_code": "MSG200"})

        self._validate_length("nm_transtorno", nm_transtorno)
        self._validate_optional("apoio_diag", apoio_diag)
        self._validate_optional("prevalencia", prevalencia)
        self._validate_optional("fatores_risco_prognostico", fatores_risco_prognostico)
        self._validate_optional("diagnostico_genero", diagnostico_genero)

        return {
            "nm_transtorno": nm_transtorno,
            "cid11": cid11,
            "apoio_diag": apoio_diag,
            "prevalencia": prevalencia,
            "fatores_risco_prognostico": fatores_risco_prognostico,
            "diagnostico_genero": diagnostico_genero,
        }

    def _normalize_disorder_update(self, disorder: Dict[str, Any]) -> Dict[str, Any]:
        nm_transtorno = normalize_and_capitalize(disorder.get("nm_transtorno"))
        cid11 = normalize_text(disorder.get("cid11"))
        apoio_diag = normalize_and_capitalize(disorder.get("apoio_diag"))
        prevalencia = normalize_and_capitalize(disorder.get("prevalencia"))
        fatores_risco_prognostico = normalize_and_capitalize(disorder.get("fatores_risco_prognostico"))
        diagnostico_genero = normalize_and_capitalize(disorder.get("diagnostico_genero"))

        if not nm_transtorno or not cid11:
            raise ValidationError(message="Missing required fields", details={"legacy_code": "MSG200"})

        self._validate_length("nm_transtorno", nm_transtorno)
        self._validate_optional("apoio_diag", apoio_diag)
        self._validate_optional("prevalencia", prevalencia)
        self._validate_optional("fatores_risco_prognostico", fatores_risco_prognostico)
        self._validate_optional("diagnostico_genero", diagnostico_genero)

        return {
            "nm_transtorno": nm_transtorno,
            "cid11": cid11,
            "apoio_diag": apoio_diag,
            "prevalencia": prevalencia,
            "fatores_risco_prognostico": fatores_risco_prognostico,
            "diagnostico_genero": diagnostico_genero,
        }

    def _normalize_subtypes(self, subtypes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        names = set()
        cids = set()
        for item in subtypes:
            nm_subtipo = normalize_and_capitalize(item.get("nm_subtipo"))
            cid11 = normalize_text(item.get("cid11"))
            obs = normalize_and_capitalize(item.get("obs"))

            if not nm_subtipo or not cid11 or not obs:
                raise ValidationError(message="Missing required fields", details={"legacy_code": "MSG200"})
            if nm_subtipo in names or cid11 in cids:
                raise ValidationError(message="Duplicate subtype in payload")
            names.add(nm_subtipo)
            cids.add(cid11)

            self._validate_subtype_length("nm_subtipo", nm_subtipo)
            self._validate_subtype_length("obs", obs)

            normalized.append({"nm_subtipo": nm_subtipo, "cid11": cid11, "obs": obs})
        return normalized

    def _normalize_severities(self, severities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        pairs = set()
        for item in severities:
            nm_gravidade = normalize_and_capitalize(item.get("nm_gravidade"))
            grav_descricao = normalize_and_capitalize(item.get("grav_descricao"))

            if not nm_gravidade or not grav_descricao:
                raise ValidationError(message="Missing required fields", details={"legacy_code": "MSG200"})
            key = (nm_gravidade, grav_descricao)
            if key in pairs:
                raise ValidationError(message="Duplicate severity in payload")
            pairs.add(key)

            self._validate_severity_length("nm_gravidade", nm_gravidade)
            self._validate_severity_length("grav_descricao", grav_descricao)

            normalized.append({"nm_gravidade": nm_gravidade, "grav_descricao": grav_descricao})
        return normalized

    def _normalize_criteria(self, criteria: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        pairs = set()
        for item in criteria:
            criterio = normalize_and_capitalize(item.get("criterio_diagnostico"))
            diferencial = item.get("criterio_diferencial")

            if not criterio:
                raise ValidationError(message="Missing required fields", details={"legacy_code": "MSG200"})
            key = (criterio, diferencial)
            if key in pairs:
                raise ValidationError(message="Duplicate criteria in payload")
            pairs.add(key)

            self._validate_criteria_length("criterio_diagnostico", criterio)

            normalized.append({"criterio_diagnostico": criterio, "criterio_diferencial": diferencial})
        return normalized

    def _validate_length(self, field: str, value: Optional[str]) -> None:
        if value is None:
            return
        limit = self._limits.get(field)
        if not limit:
            return
        if len(value) < 4 or len(value) > limit:
            raise ValidationError(message="Invalid field length", details={"legacy_code": "MSG199"})

    def _validate_optional(self, field: str, value: Optional[str]) -> None:
        if value is None:
            return
        self._validate_length(field, value)

    def _validate_subtype_length(self, field: str, value: Optional[str]) -> None:
        if value is None:
            return
        limit = self._subtype_limits.get(field)
        if limit and (len(value) < 4 or len(value) > limit):
            raise ValidationError(message="Invalid field length", details={"legacy_code": "MSG199"})

    def _validate_severity_length(self, field: str, value: Optional[str]) -> None:
        if value is None:
            return
        limit = self._severity_limits.get(field)
        if limit and (len(value) < 3 or len(value) > limit):
            raise ValidationError(message="Invalid field length", details={"legacy_code": "MSG199"})

    def _validate_criteria_length(self, field: str, value: Optional[str]) -> None:
        if value is None:
            return
        limit = self._criteria_limits.get(field)
        if limit and (len(value) < 3 or len(value) > limit):
            raise ValidationError(message="Invalid field length", details={"legacy_code": "MSG199"})
