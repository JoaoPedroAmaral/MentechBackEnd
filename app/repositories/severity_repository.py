from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.config import Config
from app.utils.database import get_connection


class SeverityRepository:
    def __init__(self) -> None:
        self._key = Config.CRYPT_PASSWORD

    def get_all(self) -> List[Dict[str, Any]]:
        sql = (
            "SELECT cd_gravidade, cd_transtorno, "
            "CAST(AES_DECRYPT(nm_gravidade, %s) AS CHAR) AS nm_gravidade, "
            "grav_descricao FROM gravidade"
        )
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id(self, severity_id: int) -> Optional[Dict[str, Any]]:
        sql = (
            "SELECT cd_gravidade, cd_transtorno, "
            "CAST(AES_DECRYPT(nm_gravidade, %s) AS CHAR) AS nm_gravidade, "
            "grav_descricao FROM gravidade WHERE cd_gravidade = %s"
        )
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, severity_id))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_by_transtorno(self, transtorno_id: int) -> List[Dict[str, Any]]:
        sql = (
            "SELECT cd_gravidade, cd_transtorno, "
            "CAST(AES_DECRYPT(nm_gravidade, %s) AS CHAR) AS nm_gravidade, "
            "grav_descricao FROM gravidade WHERE cd_transtorno = %s"
        )
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, transtorno_id))
            return cursor.fetchall()
        finally:
            conn.close()

    def exists_duplicate(
        self,
        nm_gravidade: str,
        grav_descricao: str,
        cd_transtorno: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        sql = (
            "SELECT COUNT(*) FROM gravidade WHERE nm_gravidade = AES_ENCRYPT(%s, %s) "
            "AND grav_descricao = %s AND cd_transtorno = %s"
        )
        params: list[Any] = [nm_gravidade, self._key, grav_descricao, cd_transtorno]
        if exclude_id is not None:
            sql += " AND cd_gravidade != %s"
            params.append(exclude_id)
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            (count,) = cursor.fetchone()
            return count > 0
        finally:
            conn.close()

    def create(self, nm_gravidade: str, grav_descricao: str, cd_transtorno: int) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            sql = (
                "INSERT INTO gravidade (nm_gravidade, grav_descricao, cd_transtorno) "
                "VALUES (AES_ENCRYPT(%s, %s), %s, %s)"
            )
            cursor.execute(sql, (nm_gravidade, self._key, grav_descricao, cd_transtorno))
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update(self, severity_id: int, nm_gravidade: str, grav_descricao: str, cd_transtorno: int) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            sql = (
                "UPDATE gravidade SET nm_gravidade = AES_ENCRYPT(%s, %s), "
                "grav_descricao = %s, cd_transtorno = %s WHERE cd_gravidade = %s"
            )
            cursor.execute(sql, (nm_gravidade, self._key, grav_descricao, cd_transtorno, severity_id))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete(self, severity_id: int) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gravidade WHERE cd_gravidade = %s", (severity_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_by_transtorno(self, transtorno_id: int) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gravidade WHERE cd_transtorno = %s", (transtorno_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
