from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.config import Config
from app.utils.database import get_connection

class MedicationRepository:
    def __init__(self) -> None:
        self._key = Config.CRYPT_PASSWORD

    def get_all(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT cd_medicamento, 
                   CAST(AES_DECRYPT(nm_medicamento, %s) AS CHAR) AS nm_medicamento,
                   dosagem, forma_farmaceutica, 
                   CAST(AES_DECRYPT(principio_ativo, %s) AS CHAR) AS principio_ativo,
                   fabricante
            FROM medicamento
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_patient(self, cd_paciente: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT med.cd_medicamento, 
                   CAST(AES_DECRYPT(med.nm_medicamento, %s) AS CHAR) AS nm_medicamento, 
                   pmed.cd_paciente_medicamento, pmed.dias_ministracao, pmed.dose, 
                   CAST(pmed.datas as CHAR) as datas,
                   med.dosagem, med.forma_farmaceutica,
                   CAST(AES_DECRYPT(med.principio_ativo, %s) AS CHAR) AS principio_ativo,
                   med.fabricante
            FROM medicamento med 
            JOIN paciente_medicamento pmed ON pmed.cd_medicamento = med.cd_medicamento 
            WHERE pmed.cd_paciente = %s
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key, cd_paciente))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id(self, cd_medicamento: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT cd_medicamento, 
                   CAST(AES_DECRYPT(nm_medicamento, %s) AS CHAR) AS nm_medicamento,
                   dosagem, forma_farmaceutica, 
                   CAST(AES_DECRYPT(principio_ativo, %s) AS CHAR) AS principio_ativo,
                   fabricante
            FROM medicamento 
            WHERE cd_medicamento = %s
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key, cd_medicamento))
            return cursor.fetchone()
        finally:
            conn.close()

    def check_exists(self, nm_medicamento: str, dosagem: str) -> bool:
        sql = "SELECT COUNT(*) FROM medicamento WHERE nm_medicamento = AES_ENCRYPT(%s, %s) AND dosagem = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (nm_medicamento, self._key, dosagem))
            (count,) = cursor.fetchone()
            return count > 0
        finally:
            conn.close()

    def create(self, data: Dict[str, Any]) -> int:
        sql = """
            INSERT INTO medicamento (nm_medicamento, dosagem, forma_farmaceutica, principio_ativo, fabricante) 
            VALUES (AES_ENCRYPT(%s, %s), %s, %s, AES_ENCRYPT(%s, %s), %s)
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data['nm_medicamento'], self._key,
                data['dosagem'], data.get('forma_farmaceutica'),
                data.get('principio_ativo'), self._key,
                data.get('fabricante')
            ))
            cd_medicamento = cursor.lastrowid
            conn.commit()
            return cd_medicamento
        finally:
            conn.close()

    def update(self, cd_medicamento: int, data: Dict[str, Any]) -> None:
        parts = []
        params = []
        if 'nm_medicamento' in data:
            parts.append("nm_medicamento = AES_ENCRYPT(%s, %s)")
            params.extend([data['nm_medicamento'], self._key])
        if 'dosagem' in data:
            parts.append("dosagem = %s")
            params.append(data['dosagem'])
        if 'forma_farmaceutica' in data:
            parts.append("forma_farmaceutica = %s")
            params.append(data['forma_farmaceutica'])
        if 'principio_ativo' in data:
            parts.append("principio_ativo = AES_ENCRYPT(%s, %s)")
            params.extend([data['principio_ativo'], self._key])
        if 'fabricante' in data:
            parts.append("fabricante = %s")
            params.append(data['fabricante'])

        if not parts:
            return

        sql = f"UPDATE medicamento SET {', '.join(parts)} WHERE cd_medicamento = %s"
        params.append(cd_medicamento)

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
        finally:
            conn.close()

    def delete(self, cd_medicamento: int) -> None:
        sql = "DELETE FROM medicamento WHERE cd_medicamento = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (cd_medicamento,))
            conn.commit()
        finally:
            conn.close()

    def prescribe_to_patient(self, data: dict) -> int:
        sql = "INSERT INTO paciente_medicamento(cd_paciente, cd_medicamento, dias_ministracao, dose) VALUES (%s,%s,%s,%s)"
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute(sql, (data["cd_paciente"], data["cd_medicamento"], data["dias_ministracao"], data["dose"]))
            db.commit()
            return cursor.lastrowid

    def update_prescription(self, id: int, data: dict) -> None:
        parts = []
        params = []
        for k, v in data.items():
            parts.append(f"{k} = %s")
            params.append(v)
            
        if not parts: return
        
        sql = f"UPDATE paciente_medicamento SET {','.join(parts)} WHERE cd_paciente_medicamento = %s"
        params.append(id)
        
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute(sql, tuple(params))
            db.commit()

    def delete_prescription(self, id: int) -> None:
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM paciente_medicamento WHERE cd_paciente_medicamento = %s", (id,))
            db.commit()
