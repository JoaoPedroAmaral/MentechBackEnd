from flask import jsonify
from Database.database import conectar_base_de_dados

def carregar_mensagens():
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    cursor.execute("SELECT * FROM mensagem")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def enviar_mensagem_positiva(NM_MSG):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT mensagem FROM mensagem WHERE nm_mensagem = %s", (NM_MSG,))
        mensagem = cursor.fetchone()
        bd.close()
        return mensagem
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao enviar mensagem: {e}"}),400

def enviar_mensagem_negativa(NM_MSG):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT mensagem FROM mensagem WHERE nm_mensagem = %s", (NM_MSG,))
        mensagem = cursor.fetchone()
        bd.close()
        return mensagem
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao enviar mensagem: {e}"}),400
    
#CRIEI SÓ POR DETALHE, PRETENDO CADASTRAR AS mensagem DIRETAMENTE PELO BD.
#PS:DAVI
def criar_mensagem(nm_mensagem, mensagem):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "INSERT INTO mensagem (nm_mensagem, mensagem) VALUES (%s, %s)"
        cursor.execute(sql, (nm_mensagem, mensagem))
        bd.commit()
        return jsonify({"Success":"Mensagem cadastrada com sucesso!"}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao cadastrar mensagem: {e}"}),400
    finally:
        bd.close()