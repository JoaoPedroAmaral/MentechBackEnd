from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.utils.database import get_connection

class PhoneRepository:
    def get_by_patient(self, cd_paciente: int) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM telefone WHERE cd_paciente = %s"
                cursor.execute(sql, (cd_paciente,))
                return cursor.fetchall()

    def get_by_responsible(self, cd_responsavel: int) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM telefone WHERE cd_responsavel = %s"
                cursor.execute(sql, (cd_responsavel,))
                return cursor.fetchall()

    def create(self, data: Dict[str, Any]) -> int:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO telefone (ddd, nr_telefone, tipo, cd_paciente, cd_responsavel) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    data['ddd'], 
                    data['nr_telefone'], 
                    data.get('tipo'), 
                    data.get('cd_paciente'), 
                    data.get('cd_responsavel')
                ))
                conn.commit()
                return cursor.lastrowid

    def delete_by_patient(self, cd_paciente: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "DELETE FROM telefone WHERE cd_paciente = %s"
                cursor.execute(sql, (cd_paciente,))
                conn.commit()
