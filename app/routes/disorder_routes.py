from __future__ import annotations

from flask import Blueprint

from app.schemas.disorder import (
    CriterionCreate,
    CriterionUpdate,
    DisorderAggregateCreate,
    DisorderAggregateUpdate,
    DisorderCreate,
    DisorderUpdate,
    SeverityCreate,
    SeverityUpdate,
    SubtypeCreate,
    SubtypeUpdate,
)
from app.services.criteria_service import CriteriaService
from app.services.disorder_service import DisorderService
from app.services.severity_service import SeverityService
from app.services.subtype_service import SubtypeService
from app.utils.exceptions import AppError
from app.utils.response import error, ok
from app.utils.validation import validate_schema


disorder_bp = Blueprint("disorder_bp", __name__, url_prefix="/v1")


@disorder_bp.errorhandler(AppError)
def handle_app_error(exc: AppError):
    return error(exc.message, exc.status_code, exc.details)


@disorder_bp.get("/disorders")
def list_disorders():
    service = DisorderService()
    return ok(service.get_all())


@disorder_bp.get("/disorders/details")
def list_disorders_details():
    service = DisorderService()
    return ok(service.get_all_details())


@disorder_bp.get("/disorders/<int:disorder_id>")
def get_disorder(disorder_id: int):
    service = DisorderService()
    return ok(service.get_by_id(disorder_id))


@disorder_bp.get("/disorders/<int:disorder_id>/details")
def get_disorder_details(disorder_id: int):
    service = DisorderService()
    return ok(service.get_details(disorder_id))


@disorder_bp.post("/disorders")
@validate_schema(DisorderCreate)
def create_disorder(data: DisorderCreate):
    service = DisorderService()
    disorder_id = service.create(
        nm_transtorno=data.nm_transtorno,
        cid11=data.cid11,
        apoio_diag=data.apoio_diag,
        prevalencia=data.prevalencia,
        fatores_risco_prognostico=data.fatores_risco_prognostico,
        diagnostico_genero=data.diagnostico_genero,
    )
    return ok({"id": disorder_id}, status_code=201)


@disorder_bp.post("/disorders/full")
@validate_schema(DisorderAggregateCreate)
def create_disorder_full(data: DisorderAggregateCreate):
    service = DisorderService()
    disorder_id = service.create_full(
        disorder=data.disorder.dict(),
        subtypes=[item.dict() for item in data.subtypes],
        severities=[item.dict() for item in data.severities],
        criteria=[item.dict() for item in data.criteria],
    )
    return ok({"id": disorder_id}, status_code=201)


@disorder_bp.put("/disorders/<int:disorder_id>")
@validate_schema(DisorderUpdate)
def update_disorder(disorder_id: int, data: DisorderUpdate):
    service = DisorderService()
    service.update(
        transtorno_id=disorder_id,
        nm_transtorno=data.nm_transtorno,
        cid11=data.cid11,
        apoio_diag=data.apoio_diag,
        prevalencia=data.prevalencia,
        fatores_risco_prognostico=data.fatores_risco_prognostico,
        diagnostico_genero=data.diagnostico_genero,
    )
    return ok({"id": disorder_id})


@disorder_bp.put("/disorders/<int:disorder_id>/full")
@validate_schema(DisorderAggregateUpdate)
def update_disorder_full(disorder_id: int, data: DisorderAggregateUpdate):
    service = DisorderService()
    disorder_payload = data.disorder.dict() if data.disorder is not None else None
    subtypes_payload = [item.dict() for item in data.subtypes] if data.subtypes is not None else None
    severities_payload = [item.dict() for item in data.severities] if data.severities is not None else None
    criteria_payload = [item.dict() for item in data.criteria] if data.criteria is not None else None
    service.update_full(
        transtorno_id=disorder_id,
        disorder=disorder_payload,
        subtypes=subtypes_payload,
        severities=severities_payload,
        criteria=criteria_payload,
    )
    return ok({"id": disorder_id})


@disorder_bp.delete("/disorders/<int:disorder_id>")
def delete_disorder(disorder_id: int):
    service = DisorderService()
    service.delete(disorder_id)
    return ok({"id": disorder_id})


@disorder_bp.get("/disorders/<int:disorder_id>/subtypes")
def list_subtypes(disorder_id: int):
    service = SubtypeService()
    return ok(service.get_by_transtorno(disorder_id))


@disorder_bp.post("/disorders/<int:disorder_id>/subtypes")
@validate_schema(SubtypeCreate)
def create_subtype(disorder_id: int, data: SubtypeCreate):
    service = SubtypeService()
    subtype_id = service.create(data.nm_subtipo, data.cid11, data.obs, disorder_id)
    return ok({"id": subtype_id}, status_code=201)


@disorder_bp.put("/subtypes/<int:subtype_id>")
@validate_schema(SubtypeUpdate)
def update_subtype(subtype_id: int, data: SubtypeUpdate):
    service = SubtypeService()
    service.update(subtype_id, data.nm_subtipo, data.cid11, data.obs, data.cd_transtorno)
    return ok({"id": subtype_id})


@disorder_bp.delete("/subtypes/<int:subtype_id>")
def delete_subtype(subtype_id: int):
    service = SubtypeService()
    service.delete(subtype_id)
    return ok({"id": subtype_id})


@disorder_bp.get("/disorders/<int:disorder_id>/severities")
def list_severities(disorder_id: int):
    service = SeverityService()
    return ok(service.get_by_transtorno(disorder_id))


@disorder_bp.post("/disorders/<int:disorder_id>/severities")
@validate_schema(SeverityCreate)
def create_severity(disorder_id: int, data: SeverityCreate):
    service = SeverityService()
    severity_id = service.create(data.nm_gravidade, data.grav_descricao, disorder_id)
    return ok({"id": severity_id}, status_code=201)


@disorder_bp.put("/severities/<int:severity_id>")
@validate_schema(SeverityUpdate)
def update_severity(severity_id: int, data: SeverityUpdate):
    service = SeverityService()
    service.update(severity_id, data.nm_gravidade, data.grav_descricao, data.cd_transtorno)
    return ok({"id": severity_id})


@disorder_bp.delete("/severities/<int:severity_id>")
def delete_severity(severity_id: int):
    service = SeverityService()
    service.delete(severity_id)
    return ok({"id": severity_id})


@disorder_bp.get("/disorders/<int:disorder_id>/criteria")
def list_criteria(disorder_id: int):
    service = CriteriaService()
    return ok(service.get_by_transtorno(disorder_id))


@disorder_bp.post("/disorders/<int:disorder_id>/criteria")
@validate_schema(CriterionCreate)
def create_criterion(disorder_id: int, data: CriterionCreate):
    service = CriteriaService()
    criterio_id = service.create(data.criterio_diagnostico, data.criterio_diferencial, disorder_id)
    return ok({"id": criterio_id}, status_code=201)


@disorder_bp.put("/criteria/<int:criterio_id>")
@validate_schema(CriterionUpdate)
def update_criterion(criterio_id: int, data: CriterionUpdate):
    service = CriteriaService()
    service.update(criterio_id, data.criterio_diagnostico, data.criterio_diferencial, data.cd_transtorno)
    return ok({"id": criterio_id})


@disorder_bp.delete("/criteria/<int:criterio_id>")
def delete_criterion(criterio_id: int):
    service = CriteriaService()
    service.delete(criterio_id)
    return ok({"id": criterio_id})
