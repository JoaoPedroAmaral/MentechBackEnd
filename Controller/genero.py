from flask import jsonify
from Database.database import conectar_base_de_dados
from Database.database import load_dotenv
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
import os
load_dotenv()

senha = os.getenv("CRIPT_PASSWORD")

def carregar_genero():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_genero, CAST(AES_DECRYPT(nm_genero, %s) AS CHAR) AS nm_genero FROM genero", (senha,))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def cadastrar_genero(nm_genero):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "INSERT INTO genero (nm_genero) VALUES (AES_ENCRYPT(%s, %s))"
        cursor.execute(sql, (nm_genero, senha))
        bd.commit()
        novo_cd_genero = cursor.lastrowid
        return jsonify({"MSG226":enviar_mensagem_positiva("MSG226"), "cd_genero": novo_cd_genero}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"Error":f"Erro ao cadastrar genero: {e}"}),400
    finally:
        bd.close()

def atualizar_genero(cd_genero,nm_genero=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        partes_sql = []
        valores = []
        
        if nm_genero:
            partes_sql.append("nm_genero = AES_ENCRYPT(%s, %s)")
            valores.append(nm_genero)
            valores.append(senha)

        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204")}),204

        sql = f"UPDATE genero SET {', '.join(partes_sql)} WHERE cd_genero = %s"
        valores.append(cd_genero)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return jsonify({"MSG227":enviar_mensagem_positiva("MSG227"), "cd_genero":cd_genero, "Inseridos": nm_genero}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao atualizar genero: {e}"}),400
    finally:
        bd.close()

def deletar_genero(cd_genero):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM genero WHERE cd_genero = %s"
        cursor.execute(sql, (cd_genero,))
        bd.commit()
        return jsonify({"MSG228":enviar_mensagem_positiva("MSG228"), "cd_genero":cd_genero}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao excluir genero: {e}"}),400
    finally:
        bd.close()