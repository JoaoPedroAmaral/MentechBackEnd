from __future__ import annotations
from flask import Blueprint, request
from app.services.gender_service import GenderService
from app.schemas.gender import GenderCreate, GenderUpdate
from app.utils.response import ok, error
from app.utils.validation import validate_schema

gender_v1_bp = Blueprint("gender_v1_bp", __name__, url_prefix="/v1/genders")
_service = GenderService()

@gender_v1_bp.get("")
def list_genders():
    return ok(_service.get_all())

@gender_v1_bp.post("")
@validate_schema(GenderCreate)
def create_gender(data: GenderCreate):
    gender_id = _service.create(data.nm_genero)
    return ok({"id": gender_id}, status_code=201)

@gender_v1_bp.put("/<int:cd_genero>")
@validate_schema(GenderUpdate)
def update_gender(cd_genero: int, data: GenderUpdate):
    _service.update(cd_genero, data.nm_genero)
    return ok({"id": cd_genero})

@gender_v1_bp.delete("/<int:cd_genero>")
def delete_gender(cd_genero: int):
    _service.delete(cd_genero)
    return ok({"message": "Gender removed"})
