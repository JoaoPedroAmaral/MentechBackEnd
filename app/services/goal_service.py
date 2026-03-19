from datetime import datetime, date
from app.repositories.goal_repository import GoalRepository
from app.utils.exceptions import ConflictError, ValidationError

class GoalService:
    def __init__(self):
        self._repo = GoalRepository()

    def get_by_patient(self, cd_paciente: int):
        return self._repo.get_by_patient(cd_paciente)

    def create_goal(self, data: dict):
        meta_limpa = " ".join(data["meta"].split()).capitalize()
        obs_limpa = " ".join(data["obs_meta"].split()).capitalize()
        try:
            dt_previsao_obj = datetime.strptime(data["dt_previsao"], "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Formato de data inválido. Use YYYY-MM-DD.")
            
        hoje = date.today()
        if dt_previsao_obj < hoje:
            raise ValidationError("A data de previsão não pode ser anterior a data de hoje.", code="MSG260")

        try:
            cd_meta, cd_pm = self._repo.create_atomic(
                meta=meta_limpa, 
                obs_meta=obs_limpa, 
                cd_paciente=data["cd_paciente"],
                dt_previsao=dt_previsao_obj.strftime("%Y-%m-%d"),
                dt_cadastro=hoje.strftime("%Y-%m-%d")
            )
            return {"cd_meta": cd_meta, "cd_paciente_meta": cd_pm}
        except ValueError as e:
            raise ConflictError(str(e), code="MSG211")

    def complete_goal(self, cd_paciente_meta: int):
        self._repo.complete_goal(cd_paciente_meta, date.today().strftime("%Y-%m-%d"))

    def toggle_goal(self, cd_meta: int):
        return self._repo.toggle_goal(cd_meta)

    def remove_goal(self, cd_meta: int):
        self._repo.remove_goal(cd_meta)
