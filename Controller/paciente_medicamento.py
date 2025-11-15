from flask import jsonify
from Database.database import conectar_base_de_dados
from Database.database import load_dotenv
import os
load_dotenv()

senha = os.getenv("CRIPT_PASSWORD")

def carregar_paciente_medicamento():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT * FROM paciente_medicamento")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_medicamento_por_paciente(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_paciente, cd_medicamento, CAST(AES_DECRYPT(m.nm_medicamento, %s) AS CHAR) as nm_medicamento, pm.dias_ministracao, pm.dose FROM paciente_medicamento pm LEFT JOIN medicamento m ON pm.cd_medicamento = m.cd_medicamento WHERE cd_paciente = %s", (senha, cd_paciente))
    #cursor.execute("SELECT cd_paciente, cd_medicamento, CAST(AES_DECRYPT(m.nm_medicamento, %s) AS CHAR) AS nm_medicamento, CAST(AES_DECRYPT(pm.dias_ministracao, %s) AS INT) AS dias_ministracao, CAST(AES_DECRYPT(pm.dose, %s) AS CHAR) AS dose FROM paciente_medicamento pm LEFT JOIN medicamento m ON pm.cd_medicamento = m.cd_medicamento WHERE cd_paciente = {cd_paciente}")
    linhas = cursor.fetchall()
    bd.close()
    return linhas


def criar_paciente_medicamento(cd_paciente, cd_medicamento, dias_ministracao, dose):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "INSERT INTO paciente_medicamento(cd_paciente, cd_medicamento, dias_ministracao, dose) VALUES (%s,%s,%s,%s)"
        cursor.execute(sql, (cd_paciente, cd_medicamento, dias_ministracao, dose))
        bd.commit()
        return jsonify({"Success":"Relaçao Paciente e meta criado com sucesso!"}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar relação paciente e medicamento! {e}"}),400
    finally:
        bd.close()

def atualizar_paciente_medicamento(cd_paciente_medicamento,cd_paciente=None, cd_medicamento=None, dias_ministracao=None, dose=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        partes_sql = []
        valores = []
        if cd_paciente:
            partes_sql.append("cd_paciente = %s")
            valores.append(cd_paciente)
        if cd_medicamento:
            partes_sql.append("cd_medicamento = %s")
            valores.append(cd_medicamento)
        if dias_ministracao:
            partes_sql.append("dias_ministracao = %s")
            valores.append(dias_ministracao)
        if dose:
            partes_sql.append("dose = %s")
            valores.append(dose)
        
        if not partes_sql:
            return jsonify({"Success":"Nada para atualizar"}),204

        sql = f"UPDATE paciente_medicamento SET {','.join(partes_sql)} WHERE cd_paciente_medicamento = %s"
        valores.append(cd_paciente_medicamento)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return({"Success":"Relação atualizada com sucesso!"}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao atualizar a relação: {e}"}),400
    finally:
        bd.close()

#ARRUMAR O PACIENTE_MEICAMENTO POIS O CORRETO É TER UMA PK AUTOINCREMENT E ESSES IDS, PACIENTE E MEDICAÇAO SEREM FK, CONCERTA ESSA PORRA AI
#JA ARRUMEI KRL (PS: DAVI)

#arrumar
def deletar_paciente_medicamento(cd_paciente_medicamento):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM paciente_medicamento WHERE cd_paciente_medicamento = %s"
        cursor.execute(sql, (cd_paciente_medicamento,))
        bd.commit()
        return jsonify({"Success":"Relação deletada com sucesso!"}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar relação: {e}"}),400
    finally:
        bd.close()