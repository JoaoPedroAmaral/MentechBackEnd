from __future__ import annotations

from flask import Blueprint, request

from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService
from app.utils.exceptions import AppError
from app.utils.response import error, ok
from app.utils.validation import validate_schema

user_bp = Blueprint("user_bp", __name__)
_service = UserService()


@user_bp.route("/v1/users", methods=["GET"])
def list_users():
    try:
        return ok(_service.get_all())
    except AppError as exc:
        return error(exc.message, exc.status_code, exc.details)


@user_bp.route("/v1/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    try:
        return ok(_service.get_by_id(user_id))
    except AppError as exc:
        return error(exc.message, exc.status_code, exc.details)


@user_bp.route("/v1/users", methods=["POST"])
@validate_schema(UserCreate)
def create_user(data: UserCreate):
    try:
        user_id = _service.create(
            nm_usuario=data.nm_usuario,
            senha=data.senha,
            email=data.email,
            cip=data.cip,
            confirmar_senha=data.confirmar_senha,
        )
        return ok({"cd_usuario": user_id}, 201)
    except AppError as exc:
        return error(exc.message, exc.status_code, exc.details)


@user_bp.route("/v1/users/<int:user_id>", methods=["PUT"])
@validate_schema(UserUpdate)
def update_user(user_id: int, data: UserUpdate):
    try:
        _service.update(user_id, data.nm_usuario, data.email, data.cip)
        return ok({"cd_usuario": user_id})
    except AppError as exc:
        return error(exc.message, exc.status_code, exc.details)


@user_bp.route("/v1/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    try:
        _service.delete(user_id)
        return ok({"cd_usuario": user_id})
    except AppError as exc:
        return error(exc.message, exc.status_code, exc.details)
