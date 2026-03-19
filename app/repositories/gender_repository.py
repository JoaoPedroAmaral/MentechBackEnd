from __future__ import annotations
from typing import Any, Dict, List
import os
from app.utils.database import get_connection

class GenderRepository:
    def __init__(self) -> None:
        self.senha = os.getenv("CRIPT_PASSWORD")

    def get_all(self) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT cd_genero, CAST(AES_DECRYPT(nm_genero, %s) AS CHAR) AS nm_genero FROM genero"
                cursor.execute(sql, (self.senha,))
                return cursor.fetchall()

    def create(self, nm_genero: str) -> int:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO genero (nm_genero) VALUES (AES_ENCRYPT(%s, %s))"
                cursor.execute(sql, (nm_genero, self.senha))
                conn.commit()
                return cursor.lastrowid

    def update(self, cd_genero: int, nm_genero: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "UPDATE genero SET nm_genero = AES_ENCRYPT(%s, %s) WHERE cd_genero = %s"
                cursor.execute(sql, (nm_genero, self.senha, cd_genero))
                conn.commit()

    def delete(self, cd_genero: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                sql = "DELETE FROM genero WHERE cd_genero = %s"
                cursor.execute(sql, (cd_genero,))
                conn.commit()
