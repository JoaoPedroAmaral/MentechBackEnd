from app.repositories.pathology_repository import PathologyRepository
from app.utils.text import normalize_and_capitalize

class PathologyService:
    def __init__(self):
        self._repo = PathologyRepository()

    def get_all(self):
        return self._repo.get_all()

    def get_by_patient(self, cd_paciente: int):
        return self._repo.get_by_patient(cd_paciente)

    def create_pathology(self, data: dict):
        data["doenca"] = normalize_and_capitalize(data["doenca"])
        if data.get("obs_doenca"):
            data["obs_doenca"] = normalize_and_capitalize(data["obs_doenca"])
        return self._repo.create(data)

    def update_pathology(self, id: int, data: dict):
        if "doenca" in data:
            data["doenca"] = normalize_and_capitalize(data["doenca"])
        if "obs_doenca" in data and data["obs_doenca"]:
            data["obs_doenca"] = normalize_and_capitalize(data["obs_doenca"])
        self._repo.update(id, data)

    def delete_pathology(self, id: int):
        self._repo.delete(id)
