from __future__ import annotations

from typing import Any, Dict, Optional

from app.config import Config
from app.repositories.user_repository import UserRepository
from app.utils.cache import TTLCache
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError


class UserService:
    def __init__(self, repo: Optional[UserRepository] = None) -> None:
        self._repo = repo or UserRepository()
        self._cache = TTLCache(Config.CACHE_TTL_SECONDS)

    def get_all(self) -> list[Dict[str, Any]]:
        cached = self._cache.get("users")
        if cached is not None:
            return cached
        data = self._repo.get_all()
        self._cache.set("users", data)
        return data

    def get_by_id(self, user_id: int) -> Dict[str, Any]:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(message="User not found")
        return user

    def create(self, nm_usuario: str, senha: str, email: str, cip: str, confirmar_senha: Optional[str]) -> int:
        if not nm_usuario or not senha or not email or not cip:
            raise ValidationError(message="Missing required fields")
        if confirmar_senha is not None and senha != confirmar_senha:
            raise ValidationError(message="Passwords do not match")
        if self._repo.exists_email_or_cip(email, cip):
            raise ConflictError(message="Email or CIP already exists")
        user_id = self._repo.create(nm_usuario, senha, email, cip)
        self._cache.invalidate("users")
        return user_id

    def update(self, user_id: int, nm_usuario: Optional[str], email: Optional[str], cip: Optional[str]) -> None:
        if not any([nm_usuario, email, cip]):
            raise ValidationError(message="No fields to update")
        if (email or cip) and self._repo.exists_email_or_cip(email or "", cip or "", exclude_id=user_id):
            raise ConflictError(message="Email or CIP already exists")
        self._repo.update(user_id, nm_usuario, email, cip)
        self._cache.invalidate("users")

    def delete(self, user_id: int) -> None:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(message="User not found")
        self._repo.delete(user_id)
        self._cache.invalidate("users")

    def update_password(self, user_id: int, new_password: str) -> None:
        if not new_password:
            raise ValidationError(message="Missing new password")
        self._repo.update_password(user_id, new_password)
