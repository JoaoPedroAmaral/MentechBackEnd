from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.config import Config
from app.utils.database import get_connection

class PatientRepository:
    def __init__(self) -> None:
        self._key = Config.CRYPT_PASSWORD

    def get_all(self, cd_usuario: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT p.cd_paciente, p.nm_paciente, cast(p.dt_nasc as CHAR) as dt_nascimento,
                   CAST(AES_DECRYPT(p.sexo, %s) AS CHAR) AS sexo,
                   CAST(AES_DECRYPT(g.nm_genero, %s) AS CHAR) AS nm_genero,
                   CAST(AES_DECRYPT(p.tip_sang, %s) AS CHAR) AS tip_sang,
                   prfl.perfil, p.ativo
            FROM paciente p
            LEFT JOIN genero g ON g.cd_genero = p.cd_genero
            LEFT JOIN perfil prfl ON p.cd_perfil = prfl.cd_perfil
        """
        params = [self._key, self._key, self._key]
        
        if cd_usuario:
            sql += " JOIN usuario_paciente up ON p.cd_paciente = up.cd_paciente WHERE up.cd_usuario = %s"
            params.append(cd_usuario)

        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id(self, cd_paciente: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT p.cd_paciente, p.nm_paciente, p.cd_genero, p.cd_perfil,
                   cast(p.dt_nasc as CHAR) as dt_nascimento,
                   CAST(AES_DECRYPT(p.sexo, %s) AS CHAR) AS sexo,
                   CAST(AES_DECRYPT(g.nm_genero, %s) AS CHAR) AS nm_genero,
                   CAST(AES_DECRYPT(p.tip_sang, %s) AS CHAR) AS tip_sang,
                   prfl.perfil, p.ativo
            FROM paciente p
            LEFT JOIN genero g ON g.cd_genero = p.cd_genero
            LEFT JOIN perfil prfl ON p.cd_perfil = prfl.cd_perfil
            WHERE p.cd_paciente = %s
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (self._key, self._key, self._key, cd_paciente))
            return cursor.fetchone()
        finally:
            conn.close()

    def create(self, data: Dict[str, Any], cd_usuario: int) -> int:
        sql = """
            INSERT INTO paciente (nm_paciente, dt_nasc, sexo, cd_genero, tip_sang, cd_perfil)
            VALUES (%s, %s, AES_ENCRYPT(%s, %s), %s, AES_ENCRYPT(%s, %s), %s)
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data['nm_paciente'], data['dt_nasc'], data['sexo'], self._key,
                data['cd_genero'], data['tip_sang'], self._key, data['cd_perfil']
            ))
            cd_paciente = cursor.lastrowid
            cursor.execute(
                "INSERT INTO usuario_paciente (cd_usuario, cd_paciente) VALUES (%s, %s)",
                (cd_usuario, cd_paciente)
            )
            conn.commit()
            return cd_paciente
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update(self, cd_paciente: int, data: Dict[str, Any]) -> None:
        parts = []
        params = []
        for field in ['nm_paciente', 'dt_nasc', 'cd_genero', 'cd_perfil', 'ativo']:
            if field in data and data[field] is not None:
                parts.append(f"{field} = %s")
                params.append(data[field])
        
        if 'sexo' in data and data['sexo'] is not None:
            parts.append("sexo = AES_ENCRYPT(%s, %s)")
            params.extend([data['sexo'], self._key])
            
        if 'tip_sang' in data and data['tip_sang'] is not None:
            parts.append("tip_sang = AES_ENCRYPT(%s, %s)")
            params.extend([data['tip_sang'], self._key])

        if not parts:
            return

        sql = f"UPDATE paciente SET {', '.join(parts)} WHERE cd_paciente = %s"
        params.append(cd_paciente)
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
        finally:
            conn.close()

    def update_anamnese_text(self, cd_paciente: int, text: str) -> None:
        sql = "UPDATE paciente SET ANAMNESE = %s WHERE cd_paciente = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (text, cd_paciente))
            conn.commit()
        finally:
            conn.close()
