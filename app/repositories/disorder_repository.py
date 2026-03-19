from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.config import Config
from app.utils.database import get_connection


class DuplicateError(Exception):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


class DisorderRepository:
    def __init__(self) -> None:
        self._key = Config.CRYPT_PASSWORD

    def get_all(self) -> List[Dict[str, Any]]:
        sql = (
            "SELECT t.cd_transtorno, "
            "CAST(AES_DECRYPT(t.nm_transtorno, %s) AS CHAR) AS nm_transtorno, "
            "CAST(AES_DECRYPT(c.cid11, %s) AS CHAR) AS cid11, "
            "t.apoio_diag, t.prevalencia, t.fatores_risco_prognostico, t.diagnostico_genero "
            "FROM transtorno t LEFT JOIN cid11 c ON c.cd_cid = t.cd_cid"
        )
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id(self, transtorno_id: int) -> Optional[Dict[str, Any]]:
        sql = (
            "SELECT t.cd_transtorno, "
            "CAST(AES_DECRYPT(t.nm_transtorno, %s) AS CHAR) AS nm_transtorno, "
            "CAST(AES_DECRYPT(c.cid11, %s) AS CHAR) AS cid11, "
            "t.apoio_diag, t.prevalencia, t.fatores_risco_prognostico, t.diagnostico_genero, "
            "t.cd_cid "
            "FROM transtorno t LEFT JOIN cid11 c ON c.cd_cid = t.cd_cid "
            "WHERE t.cd_transtorno = %s"
        )
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key, transtorno_id))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_all_details(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                (
                    "SELECT t.cd_transtorno, "
                    "CAST(AES_DECRYPT(t.nm_transtorno, %s) AS CHAR) AS nm_transtorno, "
                    "CAST(AES_DECRYPT(c.cid11, %s) AS CHAR) AS cid11, "
                    "t.apoio_diag, t.prevalencia, t.fatores_risco_prognostico, t.diagnostico_genero "
                    "FROM transtorno t LEFT JOIN cid11 c ON c.cd_cid = t.cd_cid"
                ),
                (self._key, self._key),
            )
            disorders = cursor.fetchall()
            if not disorders:
                return []

            ids = [row["cd_transtorno"] for row in disorders]
            placeholders = ",".join(["%s"] * len(ids))

            cursor.execute(
                (
                    "SELECT cd_subtipo, cd_transtorno, "
                    "CAST(AES_DECRYPT(nm_subtipo, %s) AS CHAR) AS nm_subtipo, "
                    "CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11, obs "
                    "FROM subtipo_transtorno st "
                    "LEFT JOIN cid11 cid ON cid.cd_cid = st.cd_cid "
                    f"WHERE cd_transtorno IN ({placeholders})"
                ),
                tuple([self._key, self._key] + ids),
            )
            subtypes = cursor.fetchall()

            cursor.execute(
                (
                    "SELECT cd_gravidade, cd_transtorno, "
                    "CAST(AES_DECRYPT(nm_gravidade, %s) AS CHAR) AS nm_gravidade, "
                    "grav_descricao FROM gravidade "
                    f"WHERE cd_transtorno IN ({placeholders})"
                ),
                tuple([self._key] + ids),
            )
            severities = cursor.fetchall()

            cursor.execute(
                (
                    "SELECT cd_criterio, cd_transtorno, "
                    "CAST(AES_DECRYPT(criterio_diagnostico, %s) AS CHAR) AS criterio_diagnostico, "
                    "criterio_diferencial FROM criterio_diagnostico "
                    f"WHERE cd_transtorno IN ({placeholders})"
                ),
                tuple([self._key] + ids),
            )
            criteria = cursor.fetchall()

            subtypes_by: Dict[int, List[Dict[str, Any]]] = {}
            for row in subtypes:
                subtypes_by.setdefault(row["cd_transtorno"], []).append(row)

            severities_by: Dict[int, List[Dict[str, Any]]] = {}
            for row in severities:
                severities_by.setdefault(row["cd_transtorno"], []).append(row)

            criteria_by: Dict[int, List[Dict[str, Any]]] = {}
            for row in criteria:
                criteria_by.setdefault(row["cd_transtorno"], []).append(row)

            for disorder in disorders:
                did = disorder["cd_transtorno"]
                disorder["subtypes"] = subtypes_by.get(did, [])
                disorder["severities"] = severities_by.get(did, [])
                disorder["criteria"] = criteria_by.get(did, [])

            return disorders
        finally:
            conn.close()

    def exists_duplicate(self, nm_transtorno: str, cid11: str, exclude_id: Optional[int] = None) -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            return self._exists_disorder(cursor, nm_transtorno, cid11, exclude_id)
        finally:
            conn.close()

    def create(
        self,
        nm_transtorno: str,
        cid11: str,
        apoio_diag: Optional[str],
        prevalencia: Optional[str],
        fatores_risco_prognostico: Optional[str],
        diagnostico_genero: Optional[str],
    ) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cid11 (cid11) VALUES (AES_ENCRYPT(%s, %s))", (cid11, self._key))
            cd_cid = cursor.lastrowid
            sql = (
                "INSERT INTO transtorno (nm_transtorno, cd_cid, apoio_diag, prevalencia, "
                "fatores_risco_prognostico, diagnostico_genero) "
                "VALUES (AES_ENCRYPT(%s, %s), %s, %s, %s, %s, %s)"
            )
            cursor.execute(
                sql,
                (
                    nm_transtorno,
                    self._key,
                    cd_cid,
                    apoio_diag,
                    prevalencia,
                    fatores_risco_prognostico,
                    diagnostico_genero,
                ),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def create_full(
        self,
        disorder: Dict[str, Any],
        subtypes: List[Dict[str, Any]],
        severities: List[Dict[str, Any]],
        criteria: List[Dict[str, Any]],
    ) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if self._exists_disorder(cursor, disorder["nm_transtorno"], disorder["cid11"]):
                raise DuplicateError("Duplicate disorder", "disorder")

            cursor.execute(
                "INSERT INTO cid11 (cid11) VALUES (AES_ENCRYPT(%s, %s))",
                (disorder["cid11"], self._key),
            )
            cd_cid = cursor.lastrowid
            cursor.execute(
                (
                    "INSERT INTO transtorno (nm_transtorno, cd_cid, apoio_diag, prevalencia, "
                    "fatores_risco_prognostico, diagnostico_genero) "
                    "VALUES (AES_ENCRYPT(%s, %s), %s, %s, %s, %s, %s)"
                ),
                (
                    disorder["nm_transtorno"],
                    self._key,
                    cd_cid,
                    disorder.get("apoio_diag"),
                    disorder.get("prevalencia"),
                    disorder.get("fatores_risco_prognostico"),
                    disorder.get("diagnostico_genero"),
                ),
            )
            transtorno_id = cursor.lastrowid

            for subtype in subtypes:
                if self._exists_subtype(cursor, subtype["nm_subtipo"], subtype["cid11"]):
                    raise DuplicateError("Duplicate subtype", "subtype")
                cursor.execute(
                    "INSERT INTO cid11 (cid11) VALUES (AES_ENCRYPT(%s, %s))",
                    (subtype["cid11"], self._key),
                )
                cd_cid = cursor.lastrowid
                cursor.execute(
                    (
                        "INSERT INTO subtipo_transtorno (nm_subtipo, cd_cid, obs, cd_transtorno) "
                        "VALUES (AES_ENCRYPT(%s, %s), %s, %s, %s)"
                    ),
                    (
                        subtype["nm_subtipo"],
                        self._key,
                        cd_cid,
                        subtype["obs"],
                        transtorno_id,
                    ),
                )

            for severity in severities:
                cursor.execute(
                    (
                        "INSERT INTO gravidade (nm_gravidade, grav_descricao, cd_transtorno) "
                        "VALUES (AES_ENCRYPT(%s, %s), %s, %s)"
                    ),
                    (
                        severity["nm_gravidade"],
                        self._key,
                        severity["grav_descricao"],
                        transtorno_id,
                    ),
                )

            for criterion in criteria:
                cursor.execute(
                    (
                        "INSERT INTO criterio_diagnostico (criterio_diagnostico, criterio_diferencial, cd_transtorno) "
                        "VALUES (AES_ENCRYPT(%s, %s), %s, %s)"
                    ),
                    (
                        criterion["criterio_diagnostico"],
                        self._key,
                        criterion.get("criterio_diferencial"),
                        transtorno_id,
                    ),
                )

            conn.commit()
            return transtorno_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update_full(
        self,
        transtorno_id: int,
        disorder: Optional[Dict[str, Any]],
        subtypes: Optional[List[Dict[str, Any]]],
        severities: Optional[List[Dict[str, Any]]],
        criteria: Optional[List[Dict[str, Any]]],
    ) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if disorder is not None:
                if self._exists_disorder(cursor, disorder["nm_transtorno"], disorder["cid11"], exclude_id=transtorno_id):
                    raise DuplicateError("Duplicate disorder", "disorder")
                cursor.execute("SELECT cd_cid FROM transtorno WHERE cd_transtorno = %s", (transtorno_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError("not_found")
                (cd_cid,) = row
                cursor.execute(
                    "UPDATE cid11 SET cid11 = AES_ENCRYPT(%s, %s) WHERE cd_cid = %s",
                    (disorder["cid11"], self._key, cd_cid),
                )
                cursor.execute(
                    (
                        "UPDATE transtorno SET nm_transtorno = AES_ENCRYPT(%s, %s), "
                        "apoio_diag = %s, prevalencia = %s, fatores_risco_prognostico = %s, "
                        "diagnostico_genero = %s WHERE cd_transtorno = %s"
                    ),
                    (
                        disorder["nm_transtorno"],
                        self._key,
                        disorder.get("apoio_diag"),
                        disorder.get("prevalencia"),
                        disorder.get("fatores_risco_prognostico"),
                        disorder.get("diagnostico_genero"),
                        transtorno_id,
                    ),
                )

            if subtypes is not None:
                cursor.execute("DELETE FROM subtipo_transtorno WHERE cd_transtorno = %s", (transtorno_id,))
                for subtype in subtypes:
                    if self._exists_subtype(cursor, subtype["nm_subtipo"], subtype["cid11"]):
                        raise DuplicateError("Duplicate subtype", "subtype")
                    cursor.execute(
                        "INSERT INTO cid11 (cid11) VALUES (AES_ENCRYPT(%s, %s))",
                        (subtype["cid11"], self._key),
                    )
                    cd_cid = cursor.lastrowid
                    cursor.execute(
                        (
                            "INSERT INTO subtipo_transtorno (nm_subtipo, cd_cid, obs, cd_transtorno) "
                            "VALUES (AES_ENCRYPT(%s, %s), %s, %s, %s)"
                        ),
                        (
                            subtype["nm_subtipo"],
                            self._key,
                            cd_cid,
                            subtype["obs"],
                            transtorno_id,
                        ),
                    )

            if severities is not None:
                cursor.execute("DELETE FROM gravidade WHERE cd_transtorno = %s", (transtorno_id,))
                for severity in severities:
                    cursor.execute(
                        (
                            "INSERT INTO gravidade (nm_gravidade, grav_descricao, cd_transtorno) "
                            "VALUES (AES_ENCRYPT(%s, %s), %s, %s)"
                        ),
                        (
                            severity["nm_gravidade"],
                            self._key,
                            severity["grav_descricao"],
                            transtorno_id,
                        ),
                    )

            if criteria is not None:
                cursor.execute("DELETE FROM criterio_diagnostico WHERE cd_transtorno = %s", (transtorno_id,))
                for criterion in criteria:
                    cursor.execute(
                        (
                            "INSERT INTO criterio_diagnostico (criterio_diagnostico, criterio_diferencial, cd_transtorno) "
                            "VALUES (AES_ENCRYPT(%s, %s), %s, %s)"
                        ),
                        (
                            criterion["criterio_diagnostico"],
                            self._key,
                            criterion.get("criterio_diferencial"),
                            transtorno_id,
                        ),
                    )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update(
        self,
        transtorno_id: int,
        cd_cid: int,
        nm_transtorno: str,
        cid11: str,
        apoio_diag: Optional[str],
        prevalencia: Optional[str],
        fatores_risco_prognostico: Optional[str],
        diagnostico_genero: Optional[str],
    ) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE cid11 SET cid11 = AES_ENCRYPT(%s, %s) WHERE cd_cid = %s",
                (cid11, self._key, cd_cid),
            )
            sql = (
                "UPDATE transtorno SET nm_transtorno = AES_ENCRYPT(%s, %s), "
                "apoio_diag = %s, prevalencia = %s, fatores_risco_prognostico = %s, "
                "diagnostico_genero = %s WHERE cd_transtorno = %s"
            )
            cursor.execute(
                sql,
                (
                    nm_transtorno,
                    self._key,
                    apoio_diag,
                    prevalencia,
                    fatores_risco_prognostico,
                    diagnostico_genero,
                    transtorno_id,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete(self, transtorno_id: int) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transtorno WHERE cd_transtorno = %s", (transtorno_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_cascade(self, transtorno_id: int) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM criterio_diagnostico WHERE cd_transtorno = %s", (transtorno_id,))
            cursor.execute("DELETE FROM gravidade WHERE cd_transtorno = %s", (transtorno_id,))
            cursor.execute("DELETE FROM subtipo_transtorno WHERE cd_transtorno = %s", (transtorno_id,))
            cursor.execute("DELETE FROM transtorno WHERE cd_transtorno = %s", (transtorno_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_details(self, transtorno_id: int) -> Dict[str, Any]:
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                (
                    "SELECT t.cd_transtorno, "
                    "CAST(AES_DECRYPT(t.nm_transtorno, %s) AS CHAR) AS nm_transtorno, "
                    "CAST(AES_DECRYPT(c.cid11, %s) AS CHAR) AS cid11, "
                    "t.apoio_diag, t.prevalencia, t.fatores_risco_prognostico, t.diagnostico_genero "
                    "FROM transtorno t LEFT JOIN cid11 c ON c.cd_cid = t.cd_cid "
                    "WHERE t.cd_transtorno = %s"
                ),
                (self._key, self._key, transtorno_id),
            )
            disorder = cursor.fetchone()
            cursor.execute(
                (
                    "SELECT cd_subtipo, cd_transtorno, "
                    "CAST(AES_DECRYPT(nm_subtipo, %s) AS CHAR) AS nm_subtipo, "
                    "CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11, obs "
                    "FROM subtipo_transtorno st "
                    "LEFT JOIN cid11 cid ON cid.cd_cid = st.cd_cid "
                    "WHERE cd_transtorno = %s"
                ),
                (self._key, self._key, transtorno_id),
            )
            subtypes = cursor.fetchall()
            cursor.execute(
                (
                    "SELECT cd_gravidade, cd_transtorno, "
                    "CAST(AES_DECRYPT(nm_gravidade, %s) AS CHAR) AS nm_gravidade, "
                    "grav_descricao FROM gravidade WHERE cd_transtorno = %s"
                ),
                (self._key, transtorno_id),
            )
            severities = cursor.fetchall()
            cursor.execute(
                (
                    "SELECT cd_criterio, cd_transtorno, "
                    "CAST(AES_DECRYPT(criterio_diagnostico, %s) AS CHAR) AS criterio_diagnostico, "
                    "criterio_diferencial FROM criterio_diagnostico WHERE cd_transtorno = %s"
                ),
                (self._key, transtorno_id),
            )
            criteria = cursor.fetchall()
            return {
                "disorder": disorder,
                "subtypes": subtypes,
                "severities": severities,
                "criteria": criteria,
            }
        finally:
            conn.close()

    def _exists_disorder(
        self,
        cursor,
        nm_transtorno: str,
        cid11: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        sql = (
            "SELECT COUNT(*) FROM transtorno t "
            "LEFT JOIN cid11 c ON c.cd_cid = t.cd_cid "
            "WHERE (t.nm_transtorno = AES_ENCRYPT(%s, %s) "
            "OR c.cid11 = AES_ENCRYPT(%s, %s))"
        )
        params = [nm_transtorno, self._key, cid11, self._key]
        if exclude_id is not None:
            sql += " AND t.cd_transtorno != %s"
            params.append(exclude_id)
        cursor.execute(sql, tuple(params))
        (count,) = cursor.fetchone()
        return count > 0

    def _exists_subtype(self, cursor, nm_subtipo: str, cid11: str) -> bool:
        sql = (
            "SELECT COUNT(*) FROM subtipo_transtorno st "
            "LEFT JOIN cid11 cid ON cid.cd_cid = st.cd_cid "
            "WHERE (st.nm_subtipo = AES_ENCRYPT(%s, %s) OR cid.cid11 = AES_ENCRYPT(%s, %s))"
        )
        cursor.execute(sql, (nm_subtipo, self._key, cid11, self._key))
        (count,) = cursor.fetchone()
        return count > 0
