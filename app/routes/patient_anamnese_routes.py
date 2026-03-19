from __future__ import annotations

from flask import Blueprint, request
from app.services.anamnese_service import AnamneseService
from app.schemas.anamnese import AnamneseGenerateRequest, AnamneseResponseSave
from app.utils.response import ok, error
from app.utils.validation import validate_schema

anamnese_bp = Blueprint("anamnese_bp", __name__, url_prefix="/v1/anamnese")
_service = AnamneseService()

@anamnese_bp.get("")
def list_anamneses():
    cd_paciente = request.args.get("cd_paciente", type=int)
    return ok(_service.list_anamneses(cd_paciente))

@anamnese_bp.get("/<int:cd_anamnese>")
def get_full(cd_anamnese: int):
    return ok(_service.get_full_anamnese(cd_anamnese))

@anamnese_bp.post("/generate")
@validate_schema(AnamneseGenerateRequest)
def generate(data: AnamneseGenerateRequest):
    return ok(_service.generate_for_patient(data.cd_paciente, data.cd_perfil), status_code=201)

@anamnese_bp.post("/answer")
@validate_schema(AnamneseResponseSave)
def answer_question(data: AnamneseResponseSave):
    _service.save_answer(data.dict())
    return ok({"message": "Answer saved successfully"}, status_code=201)

@anamnese_bp.delete("/<int:cd_anamnese>")
def delete_anamnese(cd_anamnese: int):
    _service.delete(cd_anamnese)
    return ok({"message": "Anamnese removed"})

@anamnese_bp.get("/questions/<int:cd_questao>/alternatives")
def get_alternatives(cd_questao: int):
    return ok(_service.get_question_alternatives(cd_questao))
