from flask import Blueprint, request
from app.services.pathology_service import PathologyService
from app.schemas.pathology import PathologyCreate, PathologyUpdate
from app.utils.response import ok
from app.utils.validation import validate_schema
from app.services.log_service import LogService

pathology_bp = Blueprint("pathology_bp", __name__, url_prefix="/v1/pathologies")
_service = PathologyService()

@pathology_bp.get("")
def get_pathologies():
    cd_paciente = request.args.get("cd_paciente", type=int)
    if cd_paciente:
        return ok(_service.get_by_patient(cd_paciente))
    return ok(_service.get_all())

@pathology_bp.post("")
@validate_schema(PathologyCreate)
def create_pathology(data: PathologyCreate):
    pid = _service.create_pathology(data.dict())
    LogService().register_action("CPA", cd_paciente=data.cd_paciente, adicional="Comorbidade/Patologia Anexada")
    return ok({"id": pid}, status_code=201)

@pathology_bp.put("/<int:id>")
@validate_schema(PathologyUpdate)
def update_pathology(id: int, data: PathologyUpdate):
    _service.update_pathology(id, data.dict(exclude_unset=True))
    LogService().register_action("CPA", adicional="Alteração dos detalhes patológicos")
    return ok({"id": id})

@pathology_bp.delete("/<int:id>")
def delete_pathology(id: int):
    _service.delete_pathology(id)
    return ok({"message": "Patologia apagada com sucesso"})
