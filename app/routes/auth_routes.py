from __future__ import annotations
from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest
from app.utils.response import ok
from app.utils.validation import validate_schema

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/v1/auth")
_service = AuthService()

@auth_bp.post("/login")
@validate_schema(LoginRequest)
def login(data: LoginRequest):
    user_info = _service.login(data.email, data.password)
    return ok(user_info)
