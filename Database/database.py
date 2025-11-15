import mysql.connector
from dotenv import load_dotenv
from flask import jsonify
import os


load_dotenv()

def conectar_base_de_dados():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ssl_ca_path = os.path.join(base_dir, os.getenv("DB_SSL_CA").replace("backend/", ""))

    if not os.path.exists(ssl_ca_path):
        raise FileNotFoundError(f"Certificado CA não encontrado em: {ssl_ca_path}")
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT"),
        ssl_ca=ssl_ca_path,         # Caminho do certificado CA
        ssl_verify_cert=True 
    )

def definir_usuario(cd_usuario):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    cursor.execute("SET @current_user_id = %s", (cd_usuario,))
    bd.commit()
    bd.close()
    return jsonify({"MSG": "Usuário foi deficinido com sucesso!", "cd_usuario": int(cd_usuario)})