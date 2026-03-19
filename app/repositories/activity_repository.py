from app.utils.database import get_connection

class ActivityRepository:
    def get_filtered(self, cd_paciente: int = None, cd_usuario: int = None, cd_meta: int = None):
        sql = """
            SELECT
                atv.cd_atividade, atv.cd_meta, pm.cd_paciente, up.cd_usuario,
                atv.nm_atividade, atv.descricao_atividade,
                CAST(atv.dt_atividade AS CHAR) AS dt_atividade,
                atv.parecer_tecnico, atv.resultado, atv.ativo, atv.percent_conclusao
            FROM atividade atv
            LEFT JOIN paciente_meta pm ON pm.cd_meta = atv.cd_meta
            LEFT JOIN usuario_paciente up ON up.cd_paciente = pm.cd_paciente
            WHERE 1=1
        """
        params = []
        if cd_paciente:
            sql += " AND pm.cd_paciente = %s"
            params.append(cd_paciente)
        if cd_usuario:
            sql += " AND up.cd_usuario = %s"
            params.append(cd_usuario)
        if cd_meta:
            sql += " AND atv.cd_meta = %s"
            params.append(cd_meta)

        with get_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
            
    def get_history_by_activity(self, cd_atividade: int):
        sql = """
            SELECT h.percent_conclusao, CAST(h.dt_atualizacao AS CHAR) AS dt_atualizacao, a.nm_atividade 
            FROM hst_percent_atividade h 
            JOIN atividade a ON h.cd_atividade = a.cd_atividade 
            WHERE h.cd_atividade = %s
        """
        with get_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(sql, (cd_atividade,))
            return cursor.fetchall()

    def get_history_by_goal(self, cd_meta: int):
        sql = """
            SELECT h.percent_conclusao, CAST(h.dt_atualizacao AS CHAR) AS dt_atualizacao, a.nm_atividade 
            FROM hst_percent_atividade h 
            JOIN atividade a ON h.cd_atividade = a.cd_atividade 
            WHERE a.cd_meta = %s
        """
        with get_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(sql, (cd_meta,))
            return cursor.fetchall()

    def create(self, data: dict):
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM atividade WHERE nm_atividade = %s AND descricao_atividade = %s AND cd_meta = %s",
                (data["nm_atividade"], data["descricao_atividade"], data["cd_meta"])
            )
            if cursor.fetchone()[0] > 0:
                raise ValueError("Atividade já existente para esta meta.")

            sql = "INSERT INTO atividade (nm_atividade, descricao_atividade, dt_atividade, parecer_tecnico, resultado, cd_meta) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (
                data["nm_atividade"], data["descricao_atividade"], 
                data["dt_atividade"], data["parecer_tecnico"], 
                data["resultado"], data["cd_meta"]
            ))
            cd_atividade = cursor.lastrowid
            db.commit()
            return cd_atividade

    def update(self, cd_atividade: int, data: dict):
        with get_connection() as db:
            cursor = db.cursor()
            set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
            values = list(data.values()) + [cd_atividade]
            
            sql = f"UPDATE atividade SET {set_clause} WHERE cd_atividade = %s"
            cursor.execute(sql, tuple(values))
            db.commit()
            
    def toggle_active(self, cd_atividade: int):
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT ativo FROM atividade WHERE cd_atividade = %s", (cd_atividade,))
            row = cursor.fetchone()
            if not row: raise KeyError("Atividade não encontrada.")

            novo_estado = 'N' if row[0] == 'S' else 'S'
            novo_resultado = 'Concluído' if novo_estado == 'N' else 'Em andamento'

            cursor.execute("UPDATE atividade SET ativo = %s, resultado = %s WHERE cd_atividade = %s", 
                           (novo_estado, novo_resultado, cd_atividade))
            db.commit()
            return novo_estado

    def delete(self, cd_atividade: int):
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM atividade WHERE cd_atividade = %s", (cd_atividade,))
            db.commit()
