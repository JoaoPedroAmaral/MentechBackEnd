from __future__ import annotations

from typing import Any, Dict, Optional

from flask import jsonify


def ok(data: Optional[Any] = None, status_code: int = 200):
    return jsonify({"success": True, "data": data}), status_code


def error(message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
    payload: Dict[str, Any] = {"success": False, "error": {"message": message}}
    if details:
        payload["error"]["details"] = details
    return jsonify(payload), status_code
