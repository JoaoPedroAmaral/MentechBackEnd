from typing import Any, Dict, List
from app.config import Config
from app.utils.database import get_connection

class PathologyRepository:
    def __init__(self):
        self._key = Config.CRYPT_PASSWORD

    def get_by_patient(self, cd_paciente: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT CD_PATOLOGIA as cd_patologia, cd_paciente,
                CAST(AES_DECRYPT(doenca, %s) AS CHAR) AS doenca,
                obs_doenca,
                CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11
            FROM patologia
            WHERE cd_paciente = %s
        """
        with get_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key, cd_paciente))
            return cursor.fetchall()
            
    def get_all(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT CD_PATOLOGIA as cd_patologia, cd_paciente,
                CAST(AES_DECRYPT(doenca, %s) AS CHAR) AS doenca,
                obs_doenca,
                CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11
            FROM patologia
        """
        with get_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key))
            return cursor.fetchall()

    def create(self, data: dict) -> int:
        sql = """
            INSERT INTO patologia (cd_paciente, doenca, obs_doenca, cid11)
            VALUES (%s, AES_ENCRYPT(%s, %s), %s, AES_ENCRYPT(%s, %s))
        """
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute(sql, (
                data["cd_paciente"],
                data["doenca"], self._key,
                data.get("obs_doenca", ""),
                data["cid11"], self._key
            ))
            cd_patologia = cursor.lastrowid
            db.commit()
            return cd_patologia

    def update(self, cd_patologia: int, data: dict):
        parts = []
        params = []
        if "doenca" in data:
            parts.append("doenca = AES_ENCRYPT(%s, %s)")
            params.extend([data["doenca"], self._key])
        if "obs_doenca" in data:
            parts.append("obs_doenca = %s")
            params.append(data["obs_doenca"])
        if "cid11" in data:
            parts.append("cid11 = AES_ENCRYPT(%s, %s)")
            params.extend([data["cid11"], self._key])

        if not parts: return

        sql = f"UPDATE patologia SET {', '.join(parts)} WHERE CD_PATOLOGIA = %s"
        params.append(cd_patologia)

        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute(sql, tuple(params))
            db.commit()

    def delete(self, cd_patologia: int):
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM patologia WHERE CD_PATOLOGIA = %s", (cd_patologia,))
            db.commit()
