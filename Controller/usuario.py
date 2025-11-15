from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Database.database import load_dotenv
import os
load_dotenv()
senha_encrypt = str(os.getenv("CRIPT_PASSWORD"))

def carregar_usuario():
    bd = conectar_base_de_dados()
    cursor = bd.cursor( dictionary=True)
    cursor.execute("SELECT cd_usuario, nm_usuario, CAST(AES_DECRYPT(senha, %s) AS CHAR) AS senha, email, cip FROM usuario", (senha_encrypt,))
    linhas = cursor.fetchall()
    bd.close()
    return linhas



def criar_usuario(nm_usuario, senha, email, cip):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        nm_usuario = " ".join(str(nm_usuario).split())
        nm_usuario = nm_usuario.capitalize()
#--------------------COMEÇO DAS RNs DO CREATE-------------------------------------------------
        if not nm_usuario or not email or not senha or not cip:
            return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}),400
        
        cursor.execute("SELECT email, cip FROM usuario")
        usuarios_cadastrados = cursor.fetchall()
        for (email_cadastrado, cip_cadastrado) in usuarios_cadastrados:
            if email == email_cadastrado or cip == cip_cadastrado:
                return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
            else:
                continue  
#--------------------COMEÇO DAS RNs DO CREATE-------------------------------------------------
        sql = "INSERT INTO usuario (nm_usuario, senha, email, cip) VALUES (%s, AES_ENCRYPT(%s, %s), %s, %s)"
        cursor.execute(sql, (nm_usuario, senha, senha_encrypt, email, cip))
        cd_usuario = cursor.lastrowid
        bd.commit()
        return jsonify({"MSG214": enviar_mensagem_positiva("MSG214"), "cd_usuario": cd_usuario}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar usuario: {e}"}),400
    finally:
        bd.close()

def atualizar_usuario(cd_usuario, nm_usuario=None, email=None, cip=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        partes_sql = []
        valores = []
        if nm_usuario:
            partes_sql.append("nm_usuario = %s")
            valores.append(nm_usuario)
        if email:
            partes_sql.append("email = %s")
            valores.append(email)
        if cip:
            partes_sql.append("cip = %s")
            valores.append(cip)

        if not partes_sql:
            return ({"MSG204":enviar_mensagem_positiva("MSG204")}),400
#--------------------COMEÇO DAS RNs DO UPDATE-------------------------------------------------
        if not nm_usuario or not email or not cip:
            return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}),400
        
        cursor.execute("SELECT email, cip FROM usuario WHERE cd_usuario != %s", (cd_usuario,))
        usuarios_cadastrados = cursor.fetchall()
        for (email_cadastrado, cip_cadastrado) in usuarios_cadastrados:
            if email == email_cadastrado or cip == cip_cadastrado:
                return jsonify({"MSG202": enviar_mensagem_negativa("MSG202")}),400
            else:
                continue  
#--------------------COMEÇO DAS RNs DO UPDATE-------------------------------------------------
        sql = f"UPDATE usuario SET {', '.join(partes_sql)} WHERE cd_usuario = %s"
        valores.append(cd_usuario)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return jsonify({"MSG215":enviar_mensagem_positiva("MSG215"), "cd_usuario": cd_usuario}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao atualizar o usuario: {e}"}),400

    finally:
        bd.close()

def deletar_usuario(cd_usuario):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM usuario WHERE cd_usuario = %s"
        cursor.execute(sql, (cd_usuario,))
        bd.commit()
        return jsonify({"MSG216":enviar_mensagem_positiva("MSG216")}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar usuario: {e}"}),400
    finally:
        bd.close()