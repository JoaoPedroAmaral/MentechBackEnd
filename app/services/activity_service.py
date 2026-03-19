from app.repositories.activity_repository import ActivityRepository
from app.utils.text import normalize_text
from app.utils.exceptions import ConflictError

class ActivityService:
    def __init__(self):
        self._repo = ActivityRepository()

    def get_filtered(self, cd_paciente: int = None, cd_usuario: int = None, cd_meta: int = None):
        return self._repo.get_filtered(cd_paciente, cd_usuario, cd_meta)

    def get_history(self, cd_atividade: int = None, cd_meta: int = None):
        if cd_meta:
            return self._repo.get_history_by_goal(cd_meta)
        return self._repo.get_history_by_activity(cd_atividade)

    def create_activity(self, data: dict):
        data["nm_atividade"] = normalize_text(data["nm_atividade"])
        data["descricao_atividade"] = normalize_text(data["descricao_atividade"])
        data["parecer_tecnico"] = normalize_text(data["parecer_tecnico"])
        
        try:
            return self._repo.create(data)
        except ValueError as e:
            raise ConflictError(str(e), code="MSG211")

    def update_activity(self, cd_atividade: int, data: dict):
        if not data: return
        self._repo.update(cd_atividade, data)

    def toggle_active(self, cd_atividade: int):
        return self._repo.toggle_active(cd_atividade)

    def delete_activity(self, cd_atividade: int):
        self._repo.delete(cd_atividade)
