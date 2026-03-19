from flask import Blueprint
from app.services.log_service import LogService
from app.schemas.log import LogCreate
from app.utils.response import ok
from app.utils.validation import validate_schema

log_bp = Blueprint("log_bp", __name__, url_prefix="/v1/log-actions")
_service = LogService()

@log_bp.post("")
@validate_schema(LogCreate)
def create_log(data: LogCreate):
    log_id = _service.register_log(data.dict())
    return ok({"id": log_id, "message": "Log registrado com sucesso"}, status_code=201)

@log_bp.post("/definir_usuario/<int:cd_usuario>")
def mock_definir_usuario(cd_usuario: int):
    return ok({"Usuário Declarado": cd_usuario, "aviso": "Deprecado."})
