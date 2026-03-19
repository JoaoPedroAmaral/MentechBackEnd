from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.config import Config
from app.utils.database import get_connection


class SubtypeRepository:
    def __init__(self) -> None:
        self._key = Config.CRYPT_PASSWORD

    def get_all(self) -> List[Dict[str, Any]]:
        sql = (
            "SELECT cd_subtipo, cd_transtorno, "
            "CAST(AES_DECRYPT(nm_subtipo, %s) AS CHAR) AS nm_subtipo, "
            "CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11, obs "
            "FROM subtipo_transtorno st "
            "LEFT JOIN cid11 cid ON cid.cd_cid = st.cd_cid"
        )
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id(self, subtype_id: int) -> Optional[Dict[str, Any]]:
        sql = (
            "SELECT cd_subtipo, cd_transtorno, "
            "CAST(AES_DECRYPT(nm_subtipo, %s) AS CHAR) AS nm_subtipo, "
            "CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11, obs, st.cd_cid "
            "FROM subtipo_transtorno st "
            "LEFT JOIN cid11 cid ON cid.cd_cid = st.cd_cid "
            "WHERE cd_subtipo = %s"
        )
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key, subtype_id))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_by_transtorno(self, transtorno_id: int) -> List[Dict[str, Any]]:
        sql = (
            "SELECT cd_subtipo, cd_transtorno, "
            "CAST(AES_DECRYPT(nm_subtipo, %s) AS CHAR) AS nm_subtipo, "
            "CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11, obs "
            "FROM subtipo_transtorno st "
            "LEFT JOIN cid11 cid ON cid.cd_cid = st.cd_cid "
            "WHERE cd_transtorno = %s"
        )
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key, transtorno_id))
            return cursor.fetchall()
        finally:
            conn.close()

    def exists_duplicate(
        self,
        nm_subtipo: str,
        cid11: str,
        cd_transtorno: Optional[int] = None,
        exclude_id: Optional[int] = None,
    ) -> bool:
        sql = (
            "SELECT COUNT(*) FROM subtipo_transtorno st "
            "LEFT JOIN cid11 cid ON cid.cd_cid = st.cd_cid "
            "WHERE (st.nm_subtipo = AES_ENCRYPT(%s, %s) OR cid.cid11 = AES_ENCRYPT(%s, %s))"
        )
        params: list[Any] = [nm_subtipo, self._key, cid11, self._key]
        if cd_transtorno is not None:
            sql += " AND st.cd_transtorno = %s"
            params.append(cd_transtorno)
        if exclude_id is not None:
            sql += " AND st.cd_subtipo != %s"
            params.append(exclude_id)
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            (count,) = cursor.fetchone()
            return count > 0
        finally:
            conn.close()

    def create(self, nm_subtipo: str, cid11: str, obs: str, cd_transtorno: int) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cid11 (cid11) VALUES (AES_ENCRYPT(%s, %s))", (cid11, self._key))
            cd_cid = cursor.lastrowid
            sql = (
                "INSERT INTO subtipo_transtorno (nm_subtipo, cd_cid, obs, cd_transtorno) "
                "VALUES (AES_ENCRYPT(%s, %s), %s, %s, %s)"
            )
            cursor.execute(sql, (nm_subtipo, self._key, cd_cid, obs, cd_transtorno))
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update(
        self,
        subtype_id: int,
        cd_cid: int,
        nm_subtipo: str,
        cid11: str,
        obs: str,
        cd_transtorno: int,
    ) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE cid11 SET cid11 = AES_ENCRYPT(%s, %s) WHERE cd_cid = %s",
                (cid11, self._key, cd_cid),
            )
            sql = (
                "UPDATE subtipo_transtorno SET nm_subtipo = AES_ENCRYPT(%s, %s), "
                "obs = %s, cd_transtorno = %s WHERE cd_subtipo = %s"
            )
            cursor.execute(sql, (nm_subtipo, self._key, obs, cd_transtorno, subtype_id))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete(self, subtype_id: int) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subtipo_transtorno WHERE cd_subtipo = %s", (subtype_id,))
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
            cursor.execute("DELETE FROM subtipo_transtorno WHERE cd_transtorno = %s", (transtorno_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
