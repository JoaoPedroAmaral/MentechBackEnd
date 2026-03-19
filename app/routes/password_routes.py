from __future__ import annotations

from flask import Blueprint, request

from app.schemas.password_reset import PasswordResetCreate, PasswordResetUpdate
from app.services.password_service import PasswordService
from app.utils.exceptions import AppError
from app.utils.response import error, ok
from app.utils.validation import validate_schema

password_bp = Blueprint("password_bp", __name__)
_service = PasswordService()


@password_bp.route("/v1/password-resets", methods=["GET"])
def list_password_resets():
    try:
        user_id = request.args.get("user_id", type=int)
        return ok(_service.list_requests(user_id))
    except AppError as exc:
        return error(exc.message, exc.status_code, exc.details)


@password_bp.route("/v1/password-resets", methods=["POST"])
@validate_schema(PasswordResetCreate)
def create_password_reset(data: PasswordResetCreate):
    try:
        request_id = _service.create_request(data.cd_usuario, data.email)
        return ok({"cd_alterar_senha": request_id}, 201)
    except AppError as exc:
        return error(exc.message, exc.status_code, exc.details)


@password_bp.route("/v1/password-resets/<int:request_id>", methods=["PUT"])
@validate_schema(PasswordResetUpdate)
def update_password_reset(request_id: int, data: PasswordResetUpdate):
    try:
        _service.reset_password(request_id, data.cd_usuario, data.nova_senha)
        return ok({"cd_usuario": data.cd_usuario})
    except AppError as exc:
        return error(exc.message, exc.status_code, exc.details)
