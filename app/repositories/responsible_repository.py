from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.utils.database import get_connection

class ResponsibleRepository:
    def get_by_patient_id(self, cd_paciente: int) -> List[Dict[str, Any]]:
        sql = "SELECT cd_responsavel, cd_paciente, cpf, nome, cast(dt_nascimento as CHAR) as dt_nascimento FROM responsavel WHERE cd_paciente = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (cd_paciente,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id(self, cd_responsavel: int) -> Optional[Dict[str, Any]]:
        sql = "SELECT cd_responsavel, cd_paciente, cpf, nome, cast(dt_nascimento as CHAR) as dt_nascimento FROM responsavel WHERE cd_responsavel = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (cd_responsavel,))
            return cursor.fetchone()
        finally:
            conn.close()

    def create(self, data: Dict[str, Any]) -> int:
        sql = "INSERT INTO responsavel (cd_paciente, cpf, nome, dt_nascimento) VALUES (%s, %s, %s, %s)"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (data['cd_paciente'], data['cpf'], data['nome'], data['dt_nascimento']))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def update(self, cd_responsavel: int, data: Dict[str, Any]) -> None:
        parts = []
        params = []
        for field in ["cpf", "nome", "dt_nascimento"]:
            if field in data:
                parts.append(f"{field} = %s")
                params.append(data[field])
        
        if not parts:
            return
            
        sql = f"UPDATE responsavel SET {', '.join(parts)} WHERE cd_responsavel = %s"
        params.append(cd_responsavel)
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
        finally:
            conn.close()

    def delete(self, cd_responsavel: int) -> None:
        sql = "DELETE FROM responsavel WHERE cd_responsavel = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (cd_responsavel,))
            conn.commit()
        finally:
            conn.close()

    def delete_by_patient(self, cd_paciente: int) -> None:
        sql = "DELETE FROM responsavel WHERE cd_paciente = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (cd_paciente,))
            conn.commit()
        finally:
            conn.close()
