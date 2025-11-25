from flask import jsonify
from Database.database import conectar_base_de_dados
from Database.database import load_dotenv
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
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
    cursor.execute("SELECT cd_paciente, pm.cd_medicamento, CAST(AES_DECRYPT(m.nm_medicamento, %s) AS CHAR) as nm_medicamento, pm.dias_ministracao, pm.dose FROM paciente_medicamento pm LEFT JOIN medicamento m ON pm.cd_medicamento = m.cd_medicamento WHERE cd_paciente = %s", (senha, cd_paciente))
    linhas = cursor.fetchall()
    bd.close()
    return linhas


def criar_paciente_medicamento(cd_paciente, cd_medicamento, dias_ministracao, dose):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "INSERT INTO paciente_medicamento(cd_paciente, cd_medicamento, dias_ministracao, dose) VALUES (%s,%s,%s,%s)"
        cursor.execute(sql, (cd_paciente, cd_medicamento, dias_ministracao, dose))
        cd_paciente_medicamento = cursor.lastrowid
        bd.commit()
        return jsonify({"MSG270": enviar_mensagem_positiva("MSG270"), "cd_paciente_medicamento": cd_paciente_medicamento}),201
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
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204")}),204

        sql = f"UPDATE paciente_medicamento SET {','.join(partes_sql)} WHERE cd_paciente_medicamento = %s"
        valores.append(cd_paciente_medicamento)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return({"MSG271": enviar_mensagem_positiva("MSG271")}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao atualizar a relação: {e}"}),400
    finally:
        bd.close()

def deletar_paciente_medicamento(cd_paciente_medicamento):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM paciente_medicamento WHERE cd_paciente_medicamento = %s"
        cursor.execute(sql, (cd_paciente_medicamento,))
        bd.commit()
        return jsonify({"MSG272": enviar_mensagem_positiva("MSG272"), "cd_paciente_medicamento": cd_paciente_medicamento}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar relação: {e}"}),400
    finally:
        bd.close()