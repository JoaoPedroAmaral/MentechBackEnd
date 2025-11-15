from flask import jsonify
from Database.database import conectar_base_de_dados
from Database.database import load_dotenv
import os
load_dotenv()
senha = os.getenv("CRIPT_PASSWORD")

def carregar_patologia():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""
            SELECT CD_PATOLOGIA, cd_paciente,
                CAST(AES_DECRYPT(doenca, %s) AS CHAR) AS doenca,
                obs_doenca,
                CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11
            FROM patologia
        """, (senha, senha))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_patologia_by_id(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT CD_PATOLOGIA, cd_paciente,
                CAST(AES_DECRYPT(doenca, %s) AS CHAR) AS doenca,
                obs_doenca,
                CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11
            FROM patologia
            WHERE cd_paciente = %s
        """, (senha, senha, cd_paciente))
        linhas = cursor.fetchall()
        
        if not linhas:
            print("Nenhuma patologia encontrada para o paciente.")
            return None
        return linhas
    except Exception as e:
        print(f"Erro ao carregar patologias: {e}")
        return None
    finally:
        bd.close()

def criar_patologia(cd_paciente, doenca, obs_doenca, cid11):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql ="""
        INSERT INTO patologia (cd_paciente, doenca, obs_doenca, cid11)
        VALUES (%s, AES_ENCRYPT(%s, %s), %s, AES_ENCRYPT(%s, %s))
        """
        cursor.execute(sql, (cd_paciente, doenca, senha, obs_doenca, cid11, senha))
        bd.commit()
        return jsonify({"Success": "Patologia criado com sucesso!"}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao criar transtorno: {e}"}),400
    finally:
        bd.close()


def atualizar_patologia(CD_PATOLOGIA, doenca = None, obs_doenca = None, cid11 = None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        partes_sql = []
        valores = []
        if doenca:
            partes_sql.append("doenca = AES_ENCRYPT(%s, %s)")
            valores.append(doenca)
            valores.append(senha)
        if obs_doenca:
            partes_sql.append("obs_doenca = %s")
            valores.append(obs_doenca)
        if cid11:
            partes_sql.append("cid11 = AES_ENCRYPT(%s, %s)")
            valores.append(cid11)
            valores.append(senha)
        if not partes_sql:
            print("Nada para atualizar.")
            return

        sql = f"UPDATE patologia SET {', '.join(partes_sql)} WHERE CD_PATOLOGIA = %s"
        valores.append(CD_PATOLOGIA)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return jsonify({"Success": "Transtorno atualizado com sucesso!"}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao atualizar transtorno: {e}"}),400

    finally:
        bd.close()

def deletar_patologia(CD_PATOLOGIA):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM patologia WHERE CD_PATOLOGIA = %s"
        cursor.execute(sql, (CD_PATOLOGIA,))
        bd.commit()
        return jsonify({"Success": "patologia deletada com sucesso!"}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao deletar patologia: {e}"}),400

    finally:
        bd.close()