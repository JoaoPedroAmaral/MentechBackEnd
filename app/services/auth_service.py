from __future__ import annotations
from typing import Optional, Dict, Any
from app.repositories.user_repository import UserRepository
from app.utils.exceptions import ValidationError

class AuthService:
    def __init__(self, user_repo: Optional[UserRepository] = None) -> None:
        self._user_repo = user_repo or UserRepository()

    def login(self, email: str, password: str) -> Dict[str, Any]:
        user = self._user_repo.get_auth_record(email)
        
        if not user:
            raise ValidationError("Invalid email or password")
            
        if user['senha'] != password:
            raise ValidationError("Invalid email or password")
        user.pop('senha')
        return user
