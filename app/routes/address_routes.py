from __future__ import annotations

from flask import Blueprint
from app.services.address_service import AddressService
from app.schemas.address import AddressCreate, AddressUpdate
from app.utils.response import ok
from app.utils.validation import validate_schema

address_bp = Blueprint("address_bp", __name__, url_prefix="/v1")
_service = AddressService()


@address_bp.get("/patients/<int:cd_paciente>/enderecos")
def list_enderecos(cd_paciente: int):
    return ok(_service.list_by_patient(cd_paciente))


@address_bp.post("/patients/<int:cd_paciente>/enderecos")
@validate_schema(AddressCreate)
def add_endereco(cd_paciente: int, data: AddressCreate):
    addr_id = _service.add(cd_paciente, data.dict())
    return ok({"id": addr_id}, status_code=201)


@address_bp.put("/patients/<int:cd_paciente>/enderecos/<int:cd_endereco>")
@validate_schema(AddressUpdate)
def update_endereco(cd_paciente: int, cd_endereco: int, data: AddressUpdate):
    _service.update(cd_paciente, cd_endereco, data.dict(exclude_unset=True))
    return ok({"id": cd_endereco})


@address_bp.delete("/patients/<int:cd_paciente>/enderecos/<int:cd_endereco>")
def delete_endereco(cd_paciente: int, cd_endereco: int):
    _service.remove(cd_paciente, cd_endereco)
    return ok({"id": cd_endereco})
