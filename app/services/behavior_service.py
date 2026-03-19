from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.repositories.behavior_repository import BehaviorRepository
from app.utils.text import normalize_and_capitalize
from app.utils.exceptions import ValidationError, NotFoundError
from app.utils.cache import TTLCache

class BehaviorService:
    def __init__(self, repository: Optional[BehaviorRepository] = None) -> None:
        self._repo = repository or BehaviorRepository()
        self._cache = TTLCache(300)

    def get_by_patient(self, cd_paciente: int) -> List[Dict[str, Any]]:
        cache_key = f"behavior:patient:{cd_paciente}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached
            
        behaviors = self._repo.get_all(cd_paciente)
        self._cache.set(cache_key, behaviors)
        return behaviors

    def get_all(self) -> List[Dict[str, Any]]:
        return self._repo.get_all()

    def create_behavior(self, data: Dict[str, Any]) -> int:
        text = normalize_and_capitalize(data['comportamento_paciente'])
        cd_paciente = data['cd_paciente']

        if self._repo.check_exists(text, cd_paciente):
            raise ValidationError("Behavior already registered for this patient", code="MSG211")

        data['comportamento_paciente'] = text
        behavior_id = self._repo.create(data)
        
        self._cache.invalidate(f"behavior:patient:{cd_paciente}")
        return behavior_id

    def update_behavior(self, cd_behavior: int, data: Dict[str, Any]) -> None:
        existing = self._repo.get_by_id(cd_behavior)
        if not existing:
            raise NotFoundError("Behavior not found")

        if 'comportamento_paciente' in data:
            text = normalize_and_capitalize(data['comportamento_paciente'])
            cd_paciente = data.get('cd_paciente') or existing['cd_paciente']
            
            if self._repo.check_exists(text, cd_paciente):
                raise ValidationError("Behavior already registered for this patient", code="MSG211")
            data['comportamento_paciente'] = text

        self._repo.update(cd_behavior, data)
        self._cache.invalidate(f"behavior:patient:{existing['cd_paciente']}")

    def delete_behavior(self, cd_behavior: int) -> None:
        existing = self._repo.get_by_id(cd_behavior)
        if not existing:
            raise NotFoundError("Behavior not found")
            
        self._repo.delete(cd_behavior)
        self._cache.invalidate(f"behavior:patient:{existing['cd_paciente']}")
