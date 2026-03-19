from __future__ import annotations
from typing import Any, Dict, List, Optional
import os
from app.utils.database import get_connection

class MedicalRecordRepository:
    def __init__(self) -> None:
        self.senha = os.getenv("CRIPT_PASSWORD")

    def get_all(self) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT cd_prontuario, cd_paciente, 
                           CAST(AES_DECRYPT(txt_prontuario, %s) AS CHAR) AS txt_prontuario, 
                           CAST(dt_prontuario AS CHAR) AS dt_prontuario 
                    FROM prontuario
                """
                cursor.execute(sql, (self.senha,))
                return cursor.fetchall()

    def get_by_patient(self, cd_paciente: int) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT cd_prontuario, cd_paciente, 
                           CAST(AES_DECRYPT(txt_prontuario, %s) AS CHAR) AS txt_prontuario, 
                           CAST(dt_prontuario AS CHAR) AS dt_prontuario 
                    FROM prontuario WHERE cd_paciente = %s
                """
                cursor.execute(sql, (self.senha, cd_paciente))
                return cursor.fetchall()

    def create(self, data: Dict[str, Any]) -> int:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO prontuario (cd_paciente, dt_prontuario, txt_prontuario)
                    VALUES (%s, %s, AES_ENCRYPT(%s, %s))
                """
                cursor.execute(sql, (
                    data['cd_paciente'], 
                    data['dt_prontuario'], 
                    data['txt_prontuario'], 
                    self.senha
                ))
                conn.commit()
                return cursor.lastrowid

    def update(self, cd_prontuario: int, data: Dict[str, Any]) -> None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                fields = []
                values = []
                for k, v in data.items():
                    if k == 'txt_prontuario':
                        fields.append(f"{k} = AES_ENCRYPT(%s, %s)")
                        values.extend([v, self.senha])
                    else:
                        fields.append(f"{k} = %s")
                        values.append(v)
                
                if not fields:
                    return

                sql = f"UPDATE prontuario SET {', '.join(fields)} WHERE cd_prontuario = %s"
                values.append(cd_prontuario)
                cursor.execute(sql, tuple(values))
                conn.commit()

    def delete(self, cd_prontuario: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "DELETE FROM prontuario WHERE cd_prontuario = %s"
                cursor.execute(sql, (cd_prontuario,))
                conn.commit()
