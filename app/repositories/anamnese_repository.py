from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.utils.database import get_connection

class AnamneseRepository:
    def get_all_summarized(self, cd_paciente: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT an.cd_anamnese, pa.cd_paciente, pa.nm_paciente, an.dt_anamnese
            FROM anamnese an
            JOIN paciente pa ON an.cd_paciente = pa.cd_paciente
        """
        params = []
        if cd_paciente:
            sql += " WHERE pa.cd_paciente = %s"
            params.append(cd_paciente)
            
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_full_data(self, cd_anamnese: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT an.cd_anamnese, pa.cd_paciente, pa.nm_paciente,
                   qu.cd_questao, qu.txt_questao, tq.tipo_questao,
                   aq.cd_alternativa, aq.alternativa, re.txt_resposta,
                   an.dt_anamnese
            FROM anamnese an
            JOIN paciente pa ON an.cd_paciente = pa.cd_paciente
            LEFT JOIN questao_anamnese qa ON qa.cd_anamnese = an.cd_anamnese
            LEFT JOIN questao qu ON qu.cd_questao = qa.cd_questao
            LEFT JOIN tipo_questao tq ON tq.cd_tipo_questao = qu.cd_tipo_questao
            LEFT JOIN resposta re ON re.cd_resposta = qa.cd_resposta
            LEFT JOIN alternativa_questao aq ON aq.cd_alternativa = re.cd_alternativa
            WHERE an.cd_anamnese = %s
            ORDER BY qu.cd_questao ASC
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (cd_anamnese,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_questions_by_profile(self, cd_perfil: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT q.cd_questao, q.txt_questao, q.cd_tipo_questao, q.obrigatorio,
                   tq.tipo_questao, p.perfil as perfil_questao
            FROM questao q
            JOIN tipo_questao tq ON tq.cd_tipo_questao = q.cd_tipo_questao
            JOIN perfil_questao pq ON pq.cd_questao = q.cd_questao
            JOIN perfil p ON p.cd_perfil = pq.cd_perfil
            WHERE (pq.cd_perfil = 1 OR pq.cd_perfil = %s) AND q.ativo = 'S'
            ORDER BY pq.cd_perfil ASC, q.cd_questao ASC
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (cd_perfil,))
            return cursor.fetchall()
        finally:
            conn.close()

    def create_anamnese(self, cd_paciente: int, dt_anamnese: str) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO anamnese (cd_paciente, dt_anamnese) VALUES (%s, %s)", (cd_paciente, dt_anamnese))
            cd_anamnese = cursor.lastrowid
            conn.commit()
            return cd_anamnese
        finally:
            conn.close()

    def link_question_to_anamnese(self, cd_anamnese: int, cd_questao: int) -> None:
        sql = "INSERT INTO questao_anamnese (cd_anamnese, cd_questao) VALUES (%s, %s)"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (cd_anamnese, cd_questao))
            conn.commit()
        finally:
            conn.close()

    def save_response(self, cd_questao: int, cd_anamnese: int, cd_alternativa: Optional[int] = None, txt_resposta: Optional[str] = None) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO resposta (cd_questao, cd_alternativa, txt_resposta) VALUES (%s, %s, %s)",
                (cd_questao, cd_alternativa, txt_resposta)
            )
            resp_id = cursor.lastrowid
            cursor.execute(
                "UPDATE questao_anamnese SET cd_resposta = %s WHERE cd_questao = %s AND cd_anamnese = %s AND cd_resposta IS NULL",
                (resp_id, cd_questao, cd_anamnese)
            )
            if cursor.rowcount == 0:
                 cursor.execute(
                    "INSERT INTO questao_anamnese (cd_anamnese, cd_questao, cd_resposta) VALUES (%s, %s, %s)",
                    (cd_anamnese, cd_questao, resp_id)
                )
            conn.commit()
            return resp_id
        finally:
            conn.close()

    def delete(self, cd_anamnese: int) -> None:
        sql = "DELETE FROM anamnese WHERE cd_anamnese = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (cd_anamnese,))
            conn.commit()
        finally:
            conn.close()

    def get_alternatives(self, cd_questao: int) -> List[Dict[str, Any]]:
        sql = "SELECT cd_alternativa, alternativa FROM alternativa_questao WHERE cd_questao = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (cd_questao,))
            return cursor.fetchall()
        finally:
            conn.close()
            
    def exists_active_anamnese(self, cd_paciente: int) -> bool:
        sql = "SELECT COUNT(*) FROM anamnese WHERE cd_paciente = %s"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (cd_paciente,))
            (count,) = cursor.fetchone()
            return count > 0
        finally:
            conn.close()
