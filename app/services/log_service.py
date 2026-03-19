from datetime import date
from flask import g
import logging
from app.repositories.log_repository import LogRepository

class LogService:
    def __init__(self):
        self._repo = LogRepository()

    def register_action(self, tipo_log: str, cd_paciente: int = None, cd_transtorno: int = None, cd_meta: int = None, adicional: str = None):
        user_id = getattr(g, 'user_id', None)
        
        if not user_id:
            logging.warning(f"Atenção: Ação {tipo_log} foi chamada, mas não havia usuário logado no Header. Salvando como sistema (9999).")
            user_id = 9999 
            
        base_msg = self._repo.get_log_template(tipo_log)
        final_msg = base_msg
        if adicional:
            final_msg += f" {adicional}."

        hoje = date.today().strftime("%Y-%m-%d")

        try:
            return self._repo.create(
                cd_usuario=user_id,
                tipo_log=tipo_log,
                mensagem=final_msg,
                dt_log=hoje,
                cd_paciente=cd_paciente,
                cd_transtorno=cd_transtorno,
                cd_meta=cd_meta
            )
        except Exception as e:
            logging.error(f"Erro ao persistir log: {e}")
            return None

    def register_log(self, data: dict):
        base_msg = self._repo.get_log_template(data["tipo_log"])
        
        final_msg = base_msg
        if data.get("mensagem_adicional"):
            final_msg += f" {data['mensagem_adicional']}."

        hoje = date.today().strftime("%Y-%m-%d")

        return self._repo.create(
            cd_usuario=data["cd_usuario"],
            tipo_log=data["tipo_log"],
            mensagem=final_msg,
            dt_log=hoje,
            cd_paciente=data.get("cd_paciente"),
            cd_transtorno=data.get("cd_transtorno"),
            cd_meta=data.get("cd_meta")
        )
