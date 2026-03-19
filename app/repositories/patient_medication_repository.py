from typing import Any, Dict, List
from app.utils.database import get_connection

class PatientMedicationRepository:
    def get_all(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM paciente_medicamento"
        with get_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(sql)
            return cursor.fetchall()

    def create(self, data: dict) -> int:
        sql = "INSERT INTO paciente_medicamento(cd_paciente, cd_medicamento, dias_ministracao, dose) VALUES (%s,%s,%s,%s)"
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute(sql, (data["cd_paciente"], data["cd_medicamento"], data["dias_ministracao"], data["dose"]))
            db.commit()
            return cursor.lastrowid

    def update(self, id: int, data: dict) -> None:
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

    def delete(self, id: int) -> None:
        with get_connection() as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM paciente_medicamento WHERE cd_paciente_medicamento = %s", (id,))
            db.commit()
