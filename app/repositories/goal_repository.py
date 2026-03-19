from app.utils.database import get_connection

class GoalRepository:
    def get_by_patient(self, cd_paciente: int):
        with get_connection() as db:
            cursor = db.cursor(dictionary=True)
            sql = """
                SELECT 
                    m.cd_meta, CAST(m.dt_cadastro AS CHAR) AS dt_cadastro, 
                    m.meta, m.obs_meta, m.ativo, 
                    CAST(pm.dt_previsao AS CHAR) AS dt_previsao, 
                    CAST(pm.dt_conclusao AS CHAR) AS dt_conclusao, 
                    pm.cd_paciente, pm.cd_paciente_meta
                FROM meta m 
                LEFT JOIN paciente_meta pm ON pm.cd_meta = m.cd_meta 
                WHERE pm.cd_paciente = %s
            """
            cursor.execute(sql, (cd_paciente,))
            return cursor.fetchall()

    def create_atomic(self, meta: str, obs_meta: str, cd_paciente: int, dt_previsao: str, dt_cadastro: str):
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM meta WHERE meta = %s AND obs_meta = %s", (meta, obs_meta))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Meta já existente com estas características.")
            cursor.execute("INSERT INTO meta (dt_cadastro, meta, obs_meta) VALUES (%s, %s, %s)", 
                           (dt_cadastro, meta, obs_meta))
            cd_meta = cursor.lastrowid
            cursor.execute(
                "INSERT INTO paciente_meta (cd_meta, cd_paciente, dt_previsao, dt_cadastro) VALUES (%s, %s, %s, %s)",
                (cd_meta, cd_paciente, dt_previsao, dt_cadastro)
            )
            cd_paciente_meta = cursor.lastrowid
            db.commit()
            return cd_meta, cd_paciente_meta

    def complete_goal(self, cd_paciente_meta: int, dt_conclusao: str):
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT cd_meta FROM paciente_meta WHERE cd_paciente_meta = %s", (cd_paciente_meta,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Relação Paciente-Meta não encontrada.")
            cursor.execute("UPDATE paciente_meta SET ativo = 'C', dt_conclusao = %s WHERE cd_paciente_meta = %s", 
                           (dt_conclusao, cd_paciente_meta))
            cursor.execute("UPDATE meta SET ativo = 'C' WHERE cd_meta = %s", (row[0],))
            db.commit()

    def toggle_goal(self, cd_meta: int):
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT ativo FROM meta WHERE cd_meta = %s", (cd_meta,))
            row = cursor.fetchone()
            if not row:
                raise KeyError("Meta não encontrada.")

            novo_estado = 'N' if row[0] == 'S' else 'S'
            cursor.execute("UPDATE meta SET ativo = %s WHERE cd_meta = %s", (novo_estado, cd_meta))
            db.commit()
            return novo_estado

    def remove_goal(self, cd_meta: int):
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM meta WHERE cd_meta = %s", (cd_meta,))
            db.commit()
