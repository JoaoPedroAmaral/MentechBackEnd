from app.utils.database import get_connection

class LogRepository:
    def create(self, cd_usuario: int, tipo_log: str, mensagem: str, 
               dt_log: str, cd_paciente: int = None, 
               cd_transtorno: int = None, cd_meta: int = None):
        with get_connection() as db:
            cursor = db.cursor()
            sql = """
                INSERT INTO log_acao 
                (cd_usuario, tipo_log, mensagem, dt_log, cd_paciente, cd_transtorno, cd_meta) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (cd_usuario, tipo_log, mensagem, dt_log, cd_paciente, cd_transtorno, cd_meta))
            db.commit()
            return cursor.lastrowid

    def get_log_template(self, tipo_log: str) -> str:
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT ds_positivo FROM mensagens WHERE cod_msg = %s", (tipo_log,))
            row = cursor.fetchone()
            return row[0] if row else ""
