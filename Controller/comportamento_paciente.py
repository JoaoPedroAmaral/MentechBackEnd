from flask import jsonify
from Database.database import conectar_base_de_dados
from datetime import datetime, date
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Controller.log import registrar_log
from Database.database import load_dotenv
import os
load_dotenv()
senha = os.getenv("CRIPT_PASSWORD")
tamanhos = {'comportamento_paciente': 2000}

def carregar_comportamento():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_comportamento_paciente, CAST(AES_DECRYPT(comportamento_paciente, %s) as CHAR) AS comportamento_paciente, cd_paciente from comportamento_paciente", (senha,))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_comportamento_PorPaciente(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_comportamento_paciente, CAST(AES_DECRYPT(comportamento_paciente, %s) as CHAR) AS comportamento_paciente, cd_paciente from comportamento_paciente WHERE cd_paciente = %s", (senha, cd_paciente))
    linhas = cursor.fetchall()
    bd.close()
    return linhas


def criar_comportamento(comportamento_paciente, cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        if valor == None:
            continue
        else:
            valor = " ".join(str(valor).split())
            valor = valor.capitalize()
            camposG[campo] = valor
    try:
#--------------------COMEÇO DAS RNs DO CREATE-------------------------------------------------      
        cursor.execute("SELECT COUNT(*) FROM comportamento_paciente WHERE comportamento_paciente = AES_ENCRYPT(%s, %s) AND cd_paciente = %s", (camposG['comportamento_paciente'], senha, cd_paciente))
        (existe,) = cursor.fetchone()
        if existe > 0: return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
        
        if not cd_paciente:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        for campo, valor in list(camposG.items()):
            if valor == "" or valor == None or campo not in tamanhos.keys():
                continue
            elif ((len(valor) < 5) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
#------------------FIM DAS REGRAS DE NEGÓCIO DO CREATE----------------------------------------      
        sql = "INSERT INTO comportamento_paciente (comportamento_paciente, cd_paciente) VALUES (AES_ENCRYPT(%s, %s), %s)"
        cursor.execute(sql, (comportamento_paciente, senha, cd_paciente))
        bd.commit()
        adicional = f"{comportamento_paciente}"
        #registrar_log('CCO', cd_paciente=cd_paciente, ADICIONAL=adicional)
        cd_comportamento = cursor.lastrowid 
        return jsonify({"MSG245":enviar_mensagem_positiva("MSG245"), "cd_comportamento_paciente": cd_comportamento}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar a comporamento: {e}"}),400
    finally:
        bd.close()

def atualizar_comportamento(cd_comportamento_paciente,cd_paciente=None, comportamento_paciente=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        if valor == None:
            continue
        else:
            valor = " ".join(str(valor).split())
            valor = valor.capitalize()
            camposG[campo] = valor
    try:
        partes_sql = []
        valores = []
        if comportamento_paciente:
            partes_sql.append("comportamento_paciente = AES_ENCRYPT(%s, %s)")
            valores.append(camposG['comportamento_paciente'])
            valores.append(senha)

        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204"), "cd_paciente":cd_paciente}),400
        
#--------------------COMEÇO DAS RNs DO UPDATE-------------------------------------------------      
        cursor.execute("SELECT COUNT(*) FROM comportamento_paciente WHERE comportamento_paciente = AES_ENCRYPT(%s, %s) AND cd_paciente = %s", (camposG['comportamento_paciente'], senha, cd_paciente))
        (existe,) = cursor.fetchone()
        if existe > 0: return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
        
        if not cd_paciente:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        for campo, valor in list(camposG.items()):
            if valor == "" or valor == None or campo not in tamanhos.keys():
                continue
            elif ((len(valor) < 5) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
#------------------FIM DAS REGRAS DE NEGÓCIO DO UPDATE----------------------------------------
        sql = f"UPDATE comportamento_paciente SET {', '.join(partes_sql)} WHERE cd_comportamento_paciente = %s"
        valores.append(cd_comportamento_paciente)
        cursor.execute(sql, tuple(valores))
        cursor.execute("SELECT CAST(AES_DECRYPT(comportamento_paciente, %s) AS CHAR FROM comportamento_paciente WHERE cd_comportamento_paciente = %s", (senha, cd_comportamento_paciente))
        (antigo_nome,) = cursor.fetchone()
        adicional = f"De '{antigo_nome}' para '{comportamento_paciente}'"
        #registrar_log('ADCO', cd_paciente=cd_paciente, ADICIONAL=adicional)
        bd.commit()
        return jsonify({"MSG246":enviar_mensagem_positiva("MSG246"), "cd_comportamento_paciente": cd_comportamento_paciente}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"Error":f"Erro ao atualizar comportamento: {e}"})
    finally:
        bd.close()

def deletar_comportamento(cd_comportamento_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT CAST(AES_DECRYPT(comportamento_paciente, %s) AS CHAR) as COMPORTAMENTO, cd_paciente FROM comportamento_paciente WHERE cd_comportamento_paciente = %s", (senha, cd_comportamento_paciente))
        (nome_comportamento, cd_paciente) = cursor.fetchone()
        sql = "DELETE FROM comportamento_paciente WHERE cd_comportamento_paciente = %s"
        cursor.execute(sql, (cd_comportamento_paciente,))
        bd.commit()
        adicional = f"'{nome_comportamento}' desvinculado do paciente"
        #registrar_log('RCO', cd_paciente=cd_paciente, ADICIONAL=adicional)
        return jsonify({"MSG247": enviar_mensagem_positiva("MSG247"), "cd_comportamento_paciente": cd_comportamento_paciente}),201
    except Exception as e:
        bd.rollback()
        print(f"Erro ao deletar a comportamento: {e}")
    finally:
        bd.close()