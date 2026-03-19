from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from app.repositories.anamnese_repository import AnamneseRepository
from app.utils.exceptions import ValidationError, NotFoundError, ConflictError
from app.utils.text import format_date_to_db

class AnamneseService:
    def __init__(self, repo: Optional[AnamneseRepository] = None) -> None:
        self._repo = repo or AnamneseRepository()

    def list_anamneses(self, cd_paciente: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._repo.get_all_summarized(cd_paciente)

    def get_full_anamnese(self, cd_anamnese: int) -> Dict[str, Any]:
        data = self._repo.get_full_data(cd_anamnese)
        if not data:
            raise NotFoundError("Anamnese not found")
        result = {
            "cd_anamnese": data[0]["cd_anamnese"],
            "cd_paciente": data[0]["cd_paciente"],
            "nm_paciente": data[0]["nm_paciente"],
            "dt_anamnese": data[0]["dt_anamnese"],
            "questoes": []
        }
        questions_map = {}
        for row in data:
            q_id = row["cd_questao"]
            if q_id not in questions_map:
                questions_map[q_id] = {
                    "cd_questao": q_id,
                    "txt_questao": row["txt_questao"],
                    "tipo_questao": row["tipo_questao"],
                    "respostas": []
                }
                result["questoes"].append(questions_map[q_id])
            
            if row["alternativa"]:
                questions_map[q_id]["respostas"].append({
                    "cd_alternativa": row["cd_alternativa"],
                    "alternativa": row["alternativa"]
                })
            elif row["txt_resposta"]:
                 questions_map[q_id]["respostas"].append({
                    "txt_resposta": row["txt_resposta"]
                })

        return result

    def generate_for_patient(self, cd_paciente: int, cd_perfil: int) -> Dict[str, Any]:
        if self._repo.exists_active_anamnese(cd_paciente):
            raise ConflictError("Patient already has an active anamnese")

        questions = self._repo.get_questions_by_profile(cd_perfil)
        if not questions:
            raise ValidationError("No questions found for this profile")

        hoje = datetime.now().strftime("%Y-%m-%d")
        cd_anamnese = self._repo.create_anamnese(cd_paciente, hoje)
        for q in questions:
            self._repo.link_question_to_anamnese(cd_anamnese, q["cd_questao"])
            
        return {"cd_anamnese": cd_anamnese, "questoes": questions}

    def save_answer(self, data: Dict[str, Any]) -> None:
        cd_questao = data["cd_questao"]
        cd_anamnese = data["cd_anamnese"]
        
        if data.get("cd_alternativa"):
            for alt_id in data["cd_alternativa"]:
                self._repo.save_response(cd_questao, cd_anamnese, cd_alternativa=alt_id)
        else:
            self._repo.save_response(cd_questao, cd_anamnese, txt_resposta=data.get("txt_resposta"))

    def delete(self, cd_anamnese: int) -> None:
        self._repo.delete(cd_anamnese)

    def get_question_alternatives(self, cd_questao: int) -> List[Dict[str, Any]]:
        return self._repo.get_alternatives(cd_questao)
