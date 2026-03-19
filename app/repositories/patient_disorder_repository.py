from __future__ import annotations
from typing import Any, Dict, List
from app.utils.database import get_connection

class PatientDisorderRepository:
    def get_by_patient(self, cd_paciente: int) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM paciente_transtorno WHERE cd_paciente = %s", (cd_paciente,))
                return cursor.fetchall()

    def link(self, cd_paciente: int, cd_transtorno: int, data_vinculo: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO paciente_transtorno (cd_paciente, cd_transtorno, datas) VALUES (%s, %s, %s)"
                cursor.execute(sql, (cd_paciente, cd_transtorno, data_vinculo))
                conn.commit()

    def unlink(self, cd_paciente: int, cd_transtorno: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "DELETE FROM paciente_transtorno WHERE cd_paciente = %s AND cd_transtorno = %s"
                cursor.execute(sql, (cd_paciente, cd_transtorno))
                conn.commit()

    def update(self, cd_paciente: int, cd_transtorno: int, data_vinculo: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "UPDATE paciente_transtorno SET datas = %s WHERE cd_paciente = %s AND cd_transtorno = %s"
                cursor.execute(sql, (data_vinculo, cd_paciente, cd_transtorno))
                conn.commit()

    def unlink_all(self, cd_paciente: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "DELETE FROM paciente_transtorno WHERE cd_paciente = %s"
                cursor.execute(sql, (cd_paciente,))
                conn.commit()
