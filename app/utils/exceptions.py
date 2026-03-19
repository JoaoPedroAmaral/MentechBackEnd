from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AppError(Exception):
    message: str
    status_code: int = 400
    code: str = "app_error"
    details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        if self.code.startswith("MSG"):
            return {self.code: self.message}
            
        payload = {"message": self.message, "code": self.code}
        if self.details:
            payload["details"] = self.details
        return payload


class ValidationError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, code: str = "validation_error"):
        super().__init__(message=message, status_code=400, code=code, details=details)


class NotFoundError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, code: str = "not_found"):
        super().__init__(message=message, status_code=404, code=code, details=details)


class ConflictError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, code: str = "conflict"):
        super().__init__(message=message, status_code=409, code=code, details=details)


class UnauthorizedError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, code: str = "unauthorized"):
        super().__init__(message=message, status_code=401, code=code, details=details)
