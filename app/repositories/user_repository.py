from __future__ import annotations

from typing import Any, Dict, Optional

from app.config import Config
from app.utils.database import get_connection


class UserRepository:
    def get_all(self) -> list[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT cd_usuario, nm_usuario, email, cip FROM usuario")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT cd_usuario, nm_usuario, email, cip FROM usuario WHERE cd_usuario = %s",
                (user_id,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def get_auth_record(self, email: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT cd_usuario, nm_usuario, email, cip, CAST(AES_DECRYPT(senha, %s) AS CHAR) AS senha "
                "FROM usuario WHERE email = %s",
                (Config.CRYPT_PASSWORD, email),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def exists_email_or_cip(self, email: str, cip: str, exclude_id: Optional[int] = None) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            if exclude_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM usuario WHERE (email = %s OR cip = %s) AND cd_usuario != %s",
                    (email, cip, exclude_id),
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) FROM usuario WHERE email = %s OR cip = %s",
                    (email, cip),
                )
            (count,) = cursor.fetchone()
            return count > 0
        finally:
            cursor.close()
            conn.close()

    def create(self, nm_usuario: str, senha: str, email: str, cip: str) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuario (nm_usuario, senha, email, cip) VALUES (%s, AES_ENCRYPT(%s, %s), %s, %s)",
                (nm_usuario, senha, Config.CRYPT_PASSWORD, email, cip),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    def update(self, user_id: int, nm_usuario: Optional[str], email: Optional[str], cip: Optional[str]) -> None:
        parts = []
        values: list[Any] = []
        if nm_usuario:
            parts.append("nm_usuario = %s")
            values.append(nm_usuario)
        if email:
            parts.append("email = %s")
            values.append(email)
        if cip:
            parts.append("cip = %s")
            values.append(cip)
        if not parts:
            return
        values.append(user_id)
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(f"UPDATE usuario SET {', '.join(parts)} WHERE cd_usuario = %s", tuple(values))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def delete(self, user_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM usuario WHERE cd_usuario = %s", (user_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def update_password(self, user_id: int, new_password: str) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE usuario SET senha = AES_ENCRYPT(%s, %s) WHERE cd_usuario = %s",
                (new_password, Config.CRYPT_PASSWORD, user_id),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
