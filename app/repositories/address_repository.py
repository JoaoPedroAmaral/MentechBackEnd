from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.utils.database import get_connection

class AddressRepository:
    def get_by_patient_id(self, cd_paciente: int) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM endereco WHERE cd_paciente = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (cd_paciente,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id(self, cd_endereco: int) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM endereco WHERE cd_endereco = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (cd_endereco,))
            return cursor.fetchone()
        finally:
            conn.close()

    def exists(self, cd_paciente: int, cep: str, tipo: str, cd_responsavel: Optional[int] = None, exclude_id: Optional[int] = None) -> bool:
        sql = "SELECT COUNT(*) FROM endereco WHERE cd_paciente = %s AND cep = %s AND tipo = %s"
        params = [cd_paciente, cep, tipo]
        if cd_responsavel:
            sql += " AND cd_responsavel = %s"
            params.append(cd_responsavel)
        else:
            sql += " AND cd_responsavel IS NULL"
            
        if exclude_id:
            sql += " AND cd_endereco != %s"
            params.append(exclude_id)
            
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            (count,) = cursor.fetchone()
            return count > 0
        finally:
            conn.close()

    def create(self, data: Dict[str, Any]) -> int:
        fields = ["cd_paciente", "tipo", "cd_responsavel", "cidade", "bairro", "logradouro", "cep", "uf", "complemento", "numero"]
        placeholders = ", ".join(["%s"] * len(fields))
        sql = f"INSERT INTO endereco ({', '.join(fields)}) VALUES ({placeholders})"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(data.get(f) for f in fields))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def update(self, cd_endereco: int, data: Dict[str, Any]) -> None:
        parts = []
        params = []
        for field in ["tipo", "cd_responsavel", "cidade", "bairro", "logradouro", "cep", "uf", "complemento", "numero"]:
            if field in data:
                parts.append(f"{field} = %s")
                params.append(data[field])
        
        if not parts:
            return
            
        sql = f"UPDATE endereco SET {', '.join(parts)} WHERE cd_endereco = %s"
        params.append(cd_endereco)
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            conn.commit()
        finally:
            conn.close()

    def delete(self, cd_endereco: int) -> None:
        sql = "DELETE FROM endereco WHERE cd_endereco = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (cd_endereco,))
            conn.commit()
        finally:
            conn.close()

    def delete_by_patient(self, cd_paciente: int) -> None:
        sql = "DELETE FROM endereco WHERE cd_paciente = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (cd_paciente,))
            conn.commit()
        finally:
            conn.close()
