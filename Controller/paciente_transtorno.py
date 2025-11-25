from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from datetime import datetime


def formatar_data(data):
    if "-" in data:  # Se a data contiver "-", assume "%d-%m-%Y"
        formato = "%d-%m-%Y"
    elif "/" in data:  # Se a data contiver "/", assume "%d/%m/%Y"
        formato = "%d/%m/%Y"
    else:
        raise ValueError(f"Formato de data inválido: {data}")
    
    return datetime.strptime(data, formato).strftime("%Y-%m-%d")

def carregar_paciente_transtorno():
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    cursor.execute("SELECT * FROM paciente_transtorno")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def criar_paciente_transtorno(cd_transtorno, cd_paciente, datas):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        datas = formatar_data(datetime.today().strftime('%d-%m-%Y'))
            
        sql = "INSERT INTO paciente_transtorno (cd_transtorno, cd_paciente, datas) VALUES (%s, %s, %s)"
        cursor.execute(sql, (cd_transtorno, cd_paciente, datas))
        cd_paciente_transtorno = cursor.lastrowid
        bd.commit()
        return jsonify({"MSG270": enviar_mensagem_positiva("MSG270"), "cd_paciente_transtorno": cd_paciente_transtorno}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar a relação entre paciente e transtorno: {e}"}),400
    finally:
        bd.close()

def deletar_paciente_transtorno(CD_PACIENTE_TRANSTORNO):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM paciente_transtorno WHERE CD_PACIENTE_TRANSTORNO = %s"
        cursor.execute(sql, (CD_PACIENTE_TRANSTORNO,))
        bd.commit()
        return jsonify({"MSG271": enviar_mensagem_positiva("MSG271")}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar a relação entre paciente e transtorno: {e}"}),400
    finally:
        bd.close()

def deletarTodos_paciente_transtorno(cd_transtorno):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM paciente_transtorno WHERE cd_transtorno = %s"
        cursor.execute(sql, (cd_transtorno,))
        bd.commit()
        return jsonify({"MSG271": enviar_mensagem_positiva("MSG271")}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar a relação entre paciente e transtorno: {e}"}),400
    finally:
        bd.close()