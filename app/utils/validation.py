from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Type

from flask import request
from pydantic import BaseModel, ValidationError as PydanticValidationError

from app.utils.exceptions import ValidationError


def validate_schema(schema: Type[BaseModel]) -> Callable[..., Any]:

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            payload = request.get_json(silent=True) or {}
            try:
                model = schema(**payload)
            except PydanticValidationError as exc:
                raise ValidationError(message="Invalid request body", details={"errors": exc.errors()}) from exc
            return func(*args, **kwargs, data=model)

        return wrapper

    return decorator
