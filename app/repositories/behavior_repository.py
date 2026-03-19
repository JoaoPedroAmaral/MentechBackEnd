from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.config import Config
from app.utils.database import get_connection

class BehaviorRepository:
    def __init__(self) -> None:
        self._key = Config.CRYPT_PASSWORD

    def get_all(self, cd_paciente: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT cd_comportamento_paciente, 
                   CAST(AES_DECRYPT(comportamento_paciente, %s) as CHAR) AS comportamento_paciente, 
                   cd_paciente 
            FROM comportamento_paciente
            WHERE 1=1
        """
        params = [self._key]
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

    def get_by_id(self, cd_comportamento: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT cd_comportamento_paciente, 
                   CAST(AES_DECRYPT(comportamento_paciente, %s) as CHAR) AS comportamento_paciente, 
                   cd_paciente 
            FROM comportamento_paciente 
            WHERE cd_comportamento_paciente = %s
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, cd_comportamento))
            return cursor.fetchone()
        finally:
            conn.close()

    def check_exists(self, text: str, cd_paciente: int) -> bool:
        sql = """
            SELECT COUNT(*) 
            FROM comportamento_paciente 
            WHERE comportamento_paciente = AES_ENCRYPT(%s, %s) AND cd_paciente = %s
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (text, self._key, cd_paciente))
            (count,) = cursor.fetchone()
            return count > 0
        finally:
            conn.close()

    def create(self, data: Dict[str, Any]) -> int:
        sql = """
            INSERT INTO comportamento_paciente (comportamento_paciente, cd_paciente) 
            VALUES (AES_ENCRYPT(%s, %s), %s)
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (data['comportamento_paciente'], self._key, data['cd_paciente']))
            cd_comportamento = cursor.lastrowid
            conn.commit()
            return cd_comportamento
        finally:
            conn.close()

    def update(self, cd_comportamento: int, data: Dict[str, Any]) -> None:
        parts = []
        params = []
        if 'comportamento_paciente' in data:
            parts.append("comportamento_paciente = AES_ENCRYPT(%s, %s)")
            params.extend([data['comportamento_paciente'], self._key])
        if 'cd_paciente' in data:
            parts.append("cd_paciente = %s")
            params.append(data['cd_paciente'])

        if not parts:
            return

        sql = f"UPDATE comportamento_paciente SET {', '.join(parts)} WHERE cd_comportamento_paciente = %s"
        params.append(cd_comportamento)

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
        finally:
            conn.close()

    def delete(self, cd_comportamento: int) -> None:
        sql = "DELETE FROM comportamento_paciente WHERE cd_comportamento_paciente = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (cd_comportamento,))
            conn.commit()
        finally:
            conn.close()
