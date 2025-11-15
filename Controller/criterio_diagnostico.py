from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Controller.log import registrar_log
from Database.database import load_dotenv
import os
load_dotenv()
senha = os.getenv("CRIPT_PASSWORD")

tamanhos = {'criterio_diagnostico': 2000, 'criterio_diferencial': 2, 'cd_transtorno': 9999}
def carregar_criterio_diagnostico():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_criterio, cd_transtorno, CAST(AES_DECRYPT(criterio_diagnostico, %s) AS CHAR) AS criterio_diagnostico, criterio_diferencial FROM criterio_diagnostico", (senha,))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_criterio_diagnostico_porIDTranstorno(cd_transtorno):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_criterio, cd_transtorno, CAST(AES_DECRYPT(criterio_diagnostico, %s) AS CHAR) AS criterio_diagnostico, criterio_diferencial FROM criterio_diagnostico WHERE cd_transtorno = %s",(senha, cd_transtorno))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def criar_criterio_diagnostico(criterio_diagnostico, criterio_diferencial, cd_transtorno):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        valor = " ".join(str(valor).split())
        valor = valor.capitalize()
        camposG[campo] = valor
    try:
#--------------------COMEÇO DAS RNs DO CREATE-----------------------------------
        cursor.execute("SELECT COUNT(*) FROM criterio_diagnostico WHERE criterio_diagnostico = AES_ENCRYPT(%s, %s) AND cd_transtorno = %s AND criterio_diferencial = %s", (camposG['criterio_diagnostico'], senha, cd_transtorno, camposG["criterio_diferencial"]))
        (existe,) = cursor.fetchone()
        if existe > 0: 
            return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
        
        if not criterio_diagnostico: 
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        
        if ((len(camposG['criterio_diagnostico']) < 3) or (len(camposG['criterio_diagnostico']) > tamanhos['criterio_diagnostico'])):
            return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400 
#------------------FIM DAS REGRAS DE NEGÓCIO DO CREATE----------------------------------------
        sql = "INSERT INTO criterio_diagnostico (criterio_diagnostico, criterio_diferencial, cd_transtorno) VALUES (AES_ENCRYPT(%s, %s),%s,%s)"
        cursor.execute(sql, (camposG['criterio_diagnostico'], senha, camposG['criterio_diferencial'], camposG['cd_transtorno']))
        cd_criterio = cursor.lastrowid
        bd.commit()
        adicional = f"{camposG['criterio_diagnostico']}, Diferencial? {camposG['criterio_diferencial']}. cd_criterio: {cd_criterio}"
        #Registra log de cadastro de novo critério
        #registrar_log('CCD', CD_TRANSOTRNO=cd_transtorno, ADICIONAL=adicional)
        return jsonify({"MSG218":enviar_mensagem_positiva("MSG218"), "cd_criterio": cd_criterio}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":str(e)}),500
    finally:
        bd.close()

def atualizar_criterio_diagnostico(cd_criterio,criterio_diagnostico=None, criterio_diferencial=None, cd_transtorno=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        valor = " ".join(str(valor).split())
        valor = valor.capitalize()
        camposG[campo] = valor
    
    
    try:
        partes_sql = []
        valores = []
        campos = []
        
        if criterio_diagnostico:
            partes_sql.append("criterio_diagnostico = AES_ENCRYPT(%s, %s)")
            valores.append(criterio_diagnostico)
            valores.append(senha)
            campos.append("criterio_diagnostico")
        if criterio_diferencial:
            partes_sql.append("criterio_diferencial = %s")
            valores.append(criterio_diferencial)
            campos.append("criterio_diferencial")
        if cd_transtorno:
            partes_sql.append("cd_transtorno = %s")
            valores.append(cd_transtorno)
            campos.append("cd_transtorno")

        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204")}),204

#-----------------------------COMEÇO DAS RNs DO UPDATE----------------------------------------
        if not criterio_diagnostico: 
            return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}),400
            
        if ((len(camposG['criterio_diagnostico']) < 3) or (len(camposG['criterio_diagnostico']) > tamanhos['criterio_diagnostico'])):
            return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
        
        cursor.execute("SELECT COUNT(*) FROM criterio_diagnostico WHERE criterio_diagnostico = AES_ENCRYPT(%s, %s) AND cd_transtorno = %s", (camposG['criterio_diagnostico'], senha, cd_transtorno))
        (existe,) = cursor.fetchone()
        if existe > 0: return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
#-----------------------------FIM DAS RNs DO UPDATE-------------------------------------------        
        sql = f"UPDATE criterio_diagnostico SET {', '.join(partes_sql)} WHERE cd_criterio = %s"
        valores.append(cd_criterio)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        adicional = f"para: {camposG['criterio_diagnostico']}, Diferencial? {criterio_diferencial}. cd_criterio:{cd_criterio}" 
        #registra log de alteração dos dados
        #registrar_log('ADCD', CD_TRANSOTRNO=cd_transtorno, ADICIONAL=adicional)
        return jsonify({"MSG219":enviar_mensagem_positiva("MSG219"), "cd_transtorno": cd_transtorno}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":str(e)}),500
    finally:
        bd.close()

def deletar_criterio_diagnostico(cd_criterio):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT CAST(AES_DECRYPT(criterio_diagnostico, %s) AS CHAR), cd_transtorno, criterio_diferencial FROM criterio_diagnostico WHERE cd_criterio = %s", (senha, cd_criterio))
        nome_criterio, cd_transtorno, diferencial = cursor.fetchone()
        sql = "DELETE FROM criterio_diagnostico WHERE cd_criterio = %s"
        cursor.execute(sql, (cd_criterio,))
        bd.commit()
        adicional = f"{nome_criterio}, diferencial? {diferencial}. cd_criterio:{cd_criterio}"
        #registrar_log('RCD', CD_TRANSOTRNO=cd_transtorno, ADICIONAL=adicional)
        return ({"MSG220":enviar_mensagem_positiva("MSG220"), "cd_criterio": cd_criterio}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":"Erro ao deletar criterio diagnostico: " + str(e)}),400
    finally:
        bd.close()
        
def deletarTodos_criterio_diagnostico(cd_transtorno):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM criterio_diagnostico WHERE cd_transtorno = %s"
        cursor.execute(sql, (cd_transtorno,))
        bd.commit()
        return jsonify({"MSG220":enviar_mensagem_positiva("MSG220")}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":"Erro ao deletar criterio diagnostico: " + str(e)}),400
    finally:
        bd.close()

def deletar_criterioPorIdTranstorno(cd_transtorno):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM criterio_diagnostico WHERE cd_transtorno = %s"
        cursor.execute(sql, (cd_transtorno,))
        bd.commit()
        return ({"MSG220":enviar_mensagem_positiva("MSG220")})
    except Exception as e:
        bd.rollback()
        return jsonify({"error":"Erro ao deletar criterio diagnostico: " + str(e)}),400
    finally:
        bd.close()