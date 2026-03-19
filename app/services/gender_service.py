from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.repositories.gender_repository import GenderRepository
from app.utils.text import normalize_and_capitalize
from app.utils.cache import TTLCache
from app.config import Config

class GenderService:
    CACHE_KEY = "genders:all"

    def __init__(self, repo: Optional[GenderRepository] = None) -> None:
        self._repo = repo or GenderRepository()
        self._cache = TTLCache(Config.CACHE_TTL_SECONDS)

    def get_all(self) -> List[Dict[str, Any]]:
        cached = self._cache.get(self.CACHE_KEY)
        if cached:
            return cached
        
        genders = self._repo.get_all()
        self._cache.set(self.CACHE_KEY, genders)
        return genders

    def create(self, nm_genero: str) -> int:
        nm_genero = normalize_and_capitalize(nm_genero)
        cd_genero = self._repo.create(nm_genero)
        self._cache.invalidate(self.CACHE_KEY)
        return cd_genero

    def update(self, cd_genero: int, nm_genero: str) -> None:
        nm_genero = normalize_and_capitalize(nm_genero)
        self._repo.update(cd_genero, nm_genero)
        self._cache.invalidate(self.CACHE_KEY)

    def delete(self, cd_genero: int) -> None:
        self._repo.delete(cd_genero)
        self._cache.invalidate(self.CACHE_KEY)
