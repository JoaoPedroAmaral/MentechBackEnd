from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.config import Config
from app.utils.database import get_connection


class CriteriaRepository:
    def __init__(self) -> None:
        self._key = Config.CRYPT_PASSWORD

    def get_all(self) -> List[Dict[str, Any]]:
        sql = (
            "SELECT cd_criterio, cd_transtorno, "
            "CAST(AES_DECRYPT(criterio_diagnostico, %s) AS CHAR) AS criterio_diagnostico, "
            "criterio_diefrencial FROM criterio_diagnostico"
        )
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id(self, criterio_id: int) -> Optional[Dict[str, Any]]:
        sql = (
            "SELECT cd_criterio, cd_transtorno, "
            "CAST(AES_DECRYPT(criterio_diagnostico, %s) AS CHAR) AS criterio_diagnostico, "
            "criterio_diferencial FROM criterio_diagnostico WHERE cd_criterio = %s"
        )
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, criterio_id))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_by_transtorno(self, transtorno_id: int) -> List[Dict[str, Any]]:
        sql = (
            "SELECT cd_criterio, cd_transtorno, "
            "CAST(AES_DECRYPT(criterio_diagnostico, %s) AS CHAR) AS criterio_diagnostico, "
            "criterio_diferencial FROM criterio_diagnostico WHERE cd_transtorno = %s"
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
        criterio_diagnostico: str,
        criterio_diferencial: Optional[str],
        cd_transtorno: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        sql = (
            "SELECT COUNT(*) FROM criterio_diagnostico WHERE criterio_diagnostico = AES_ENCRYPT(%s, %s) "
            "AND cd_transtorno = %s AND criterio_diferencial = %s"
        )
        params: list[Any] = [criterio_diagnostico, self._key, cd_transtorno, criterio_diferencial]
        if exclude_id is not None:
            sql += " AND cd_criterio != %s"
            params.append(exclude_id)
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            (count,) = cursor.fetchone()
            return count > 0
        finally:
            conn.close()

    def create(self, criterio_diagnostico: str, criterio_diferencial: Optional[str], cd_transtorno: int) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            sql = (
                "INSERT INTO criterio_diagnostico (criterio_diagnostico, criterio_diferencial, cd_transtorno) "
                "VALUES (AES_ENCRYPT(%s, %s), %s, %s)"
            )
            cursor.execute(sql, (criterio_diagnostico, self._key, criterio_diferencial, cd_transtorno))
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update(
        self,
        criterio_id: int,
        criterio_diagnostico: str,
        criterio_diferencial: Optional[str],
        cd_transtorno: int,
    ) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            sql = (
                "UPDATE criterio_diagnostico SET criterio_diagnostico = AES_ENCRYPT(%s, %s), "
                "criterio_diferencial = %s, cd_transtorno = %s WHERE cd_criterio = %s"
            )
            cursor.execute(sql, (criterio_diagnostico, self._key, criterio_diferencial, cd_transtorno, criterio_id))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete(self, criterio_id: int) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM criterio_diagnostico WHERE cd_criterio = %s", (criterio_id,))
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
            cursor.execute("DELETE FROM criterio_diagnostico WHERE cd_transtorno = %s", (transtorno_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
