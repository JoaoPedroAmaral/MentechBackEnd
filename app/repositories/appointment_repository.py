from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import date, time
from app.utils.database import get_connection

class AppointmentRepository:
    def get_all(self, cd_usuario: Optional[int] = None, cd_paciente: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT cd_agendamento, cd_usuario, cd_paciente, 
                   CAST(dt_agendamento AS CHAR) AS dt_agendamento,
                   CAST(hora_inicio AS CHAR) AS hora_inicio,
                   CAST(hora_fim AS CHAR) AS hora_fim,
                   comparecimento
            FROM agendamento
            WHERE 1=1
        """
        params = []
        if cd_usuario:
            sql += " AND cd_usuario = %s"
            params.append(cd_usuario)
        if cd_paciente:
            sql += " AND cd_paciente = %s"
            params.append(cd_paciente)

        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id(self, cd_agendamento: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT cd_agendamento, cd_usuario, cd_paciente, 
                   CAST(dt_agendamento AS CHAR) AS dt_agendamento,
                   CAST(hora_inicio AS CHAR) AS hora_inicio,
                   CAST(hora_fim AS CHAR) AS hora_fim,
                   comparecimento
            FROM agendamento
            WHERE cd_agendamento = %s
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (cd_agendamento,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_conflicts(self, cd_usuario: int, dt_agendamento: date, ignore_id: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT CAST(hora_inicio AS CHAR) AS hora_inicio, CAST(hora_fim AS CHAR) AS hora_fim 
            FROM agendamento 
            WHERE dt_agendamento = %s AND cd_usuario = %s
        """
        params = [dt_agendamento, cd_usuario]
        if ignore_id:
            sql += " AND cd_agendamento != %s"
            params.append(ignore_id)

        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            conn.close()

    def create(self, data: Dict[str, Any]) -> int:
        sql = """
            INSERT INTO agendamento (cd_usuario, cd_paciente, dt_agendamento, hora_inicio, hora_fim, comparecimento)
            VALUES (%s, %s, %s, %s, %s, 'N')
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data['cd_usuario'], data['cd_paciente'], data['dt_agendamento'],
                data['hora_inicio'], data['hora_fim']
            ))
            cd_agendamento = cursor.lastrowid
            conn.commit()
            return cd_agendamento
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update(self, cd_agendamento: int, data: Dict[str, Any]) -> None:
        parts = []
        params = []
        for field in ['dt_agendamento', 'hora_inicio', 'hora_fim', 'cd_usuario', 'cd_paciente', 'comparecimento']:
            if field in data and data[field] is not None:
                parts.append(f"{field} = %s")
                params.append(data[field])

        if not parts:
            return

        sql = f"UPDATE agendamento SET {', '.join(parts)} WHERE cd_agendamento = %s"
        params.append(cd_agendamento)

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete(self, cd_agendamento: int) -> None:
        sql = "DELETE FROM agendamento WHERE cd_agendamento = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (cd_agendamento,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
