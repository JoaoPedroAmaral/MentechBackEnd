from __future__ import annotations

from typing import Any, Dict, Optional

from app.config import Config
from app.utils.database import get_connection


class PasswordResetRepository:
    def get_all(self) -> list[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT cd_alterar_senha, cd_usuario, email, CAST(AES_DECRYPT(token, %s) AS CHAR) AS token, "
                "utilizado, CAST(ti_validade AS CHAR) AS ti_validade, CAST(timestamp AS CHAR) AS timestamp "
                "FROM alterar_senha",
                (Config.CRYPT_PASSWORD,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_by_user(self, user_id: int) -> list[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT cd_alterar_senha, cd_usuario, email, CAST(AES_DECRYPT(token, %s) AS CHAR) AS token, "
                "utilizado, CAST(ti_validade AS CHAR) AS ti_validade, CAST(timestamp AS CHAR) AS timestamp "
                "FROM alterar_senha WHERE cd_usuario = %s",
                (Config.CRYPT_PASSWORD, user_id),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def create(self, user_id: int, email: str, token: str) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO alterar_senha (cd_usuario, email, token, utilizado) VALUES (%s, %s, AES_ENCRYPT(%s, %s), 'N')",
                (user_id, email, token, Config.CRYPT_PASSWORD),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    def get_token_info(self, request_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT cd_alterar_senha, utilizado, CAST(ti_validade AS CHAR) AS ti_validade, "
                "CAST(timestamp AS CHAR) AS timestamp FROM alterar_senha WHERE cd_alterar_senha = %s",
                (request_id,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def mark_used(self, request_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE alterar_senha SET utilizado = 'S' WHERE cd_alterar_senha = %s",
                (request_id,),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
