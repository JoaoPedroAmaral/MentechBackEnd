from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Controller.log import registrar_log
from Database.database import load_dotenv
import os
load_dotenv()
senha = os.getenv("CRIPT_PASSWORD")

tamanhos = {'nm_gravidade': 255, 'grav_descricao': 200, 'cd_transtorno': 9999}
def carregar_gravidade():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_gravidade, cd_transtorno, CAST(AES_DECRYPT(nm_gravidade, %s) AS CHAR) AS nm_gravidade, grav_descricao FROM gravidade",(senha,))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_gravidade_PorIdTranstorno(id):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_gravidade, cd_transtorno, CAST(AES_DECRYPT(nm_gravidade, %s) AS CHAR) AS nm_gravidade, grav_descricao FROM gravidade WHERE cd_transtorno = %s", (senha, id))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def criar_gravidade(nm_gravidade, grav_descricao, cd_transtorno):
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
#--------------------COMEÇO DAS RNs DO CREATE-----------------------------------
        cursor.execute("SELECT COUNT(*) FROM gravidade WHERE nm_gravidade = AES_ENCRYPT(%s, %s) AND grav_descricao = %s AND cd_transtorno = %s", (camposG['nm_gravidade'], senha, camposG['grav_descricao'], cd_transtorno))
        (existe,) = cursor.fetchone()
        if existe > 0: return jsonify({"MSG201": enviar_mensagem_negativa("MSG201")}),400
        
        if any(valor == " " or valor == None for valor in camposG.values()): return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}),400

        for campo, valor in list(camposG.items())[:-1]:
            if valor == "" or valor == None:
                continue
            elif ((len(valor) < 3) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400 
#--------------------COMEÇO DAS RNs DO CREATE-----------------------------------
        valores = list(camposG.values())
        sql = "INSERT INTO gravidade (nm_gravidade, grav_descricao, cd_transtorno) VALUES (AES_ENCRYPT(%s, %s), %s, %s)"
        cursor.execute(sql,(camposG["nm_gravidade"], senha, camposG["grav_descricao"], cd_transtorno))
        cd_gravidade = cursor.lastrowid
        bd.commit()
        #Registro de log
        adicional = f"{camposG['nm_gravidade']}. cd_gravidade: {cd_gravidade}"
        #registrar_log('CGR', CD_TRANSOTRNO=cd_transtorno, ADICIONAL=adicional)
        return jsonify({"MSG221":enviar_mensagem_positiva("MSG221"), "cd_gravidade": cd_gravidade}),201 
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar gravidade: {e}"}),400
    finally:
        bd.close()

def atualizar_gravidade(cd_gravidade,nm_gravidade=None, grav_descricao=None, cd_transtorno=None):
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
        campos = []
                
        if nm_gravidade:
            partes_sql.append("nm_gravidade = AES_ENCRYPT(%s, %s)")
            valores.append(nm_gravidade)
            valores.append(senha)
            campos.append("nm_gravidade")
        if grav_descricao:
            partes_sql.append("grav_descricao = %s")
            valores.append(grav_descricao)
            campos.append("grav_descricao")
        if cd_transtorno:
            partes_sql.append("cd_transtorno = %s")
            valores.append(cd_transtorno)
            campos.append("cd_transtorno")

        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204")}),204

#-----------------------------COMEÇO DAS RNs DO UPDATE----------------------------------------
        if any(valor == "''" for valor in camposG.values()): return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}),400
        
        for i in range(len(valores)):
            valor = valores[i]
            valor = " ".join(str(valor).split())     
            valor = valor.capitalize()        
            valores[i] = valor
        
        for campo, valor in list(camposG.items())[1:]:
            if valor == "''" or valor == None:
                continue
            elif((len(valor) < 4) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199": enviar_mensagem_negativa("MSG199")}),400
            
        cursor.execute("SELECT COUNT(*) FROM gravidade WHERE nm_gravidade = AES_ENCRYPT(%s, %s) AND grav_descricao = %s AND cd_transtorno = %s", (camposG['nm_gravidade'], senha, camposG['grav_descricao'], cd_transtorno))
        (existe,) = cursor.fetchone()
        if existe > 0: return jsonify({"MSG201": enviar_mensagem_negativa("MSG201")}),400   
#-----------------------------FIM DAS RNs DO UPDATE-------------------------------------------              
        sql = f"UPDATE gravidade SET {', '.join(partes_sql)} WHERE cd_gravidade = %s"
        valores.append(cd_gravidade)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        #Registra log
        adicional = f"'{camposG['nm_gravidade']}', cd_gravidade: {cd_gravidade}"
        #registrar_log('ADGR', CD_TRANSOTRNO=cd_transtorno, ADICIONAL=adicional)
        return jsonify({"MSG222":enviar_mensagem_positiva("MSG222"), "cd_gravidade": cd_gravidade}),201 
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao atualizar gravidade: {e}"}),400
    finally:
        bd.close()

def deletar_gravidade(cd_gravidade):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT cd_transtorno, nm_gravidade FROM gravidade WHERE cd_gravidade = %s", (cd_gravidade,))
        cd_transtorno, nm_gravidade = cursor.fetchone()
        sql = "DELETE FROM gravidade WHERE cd_gravidade = %s"
        cursor.execute(sql, (cd_gravidade,))
        bd.commit()
        #Registra_log
        adicional = f"'{nm_gravidade}', cd_gravidade: {cd_gravidade}"
        #registrar_log('RGR', CD_TRANSOTRNO=cd_transtorno, ADICIONAL=adicional)
        return jsonify({"MSG223":enviar_mensagem_positiva("MSG223"), "cd_gravidade": cd_gravidade}),201 
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar gravidade: {e}"}),400
    finally:
        bd.close()

def deletarTodos_gravidade(cd_transtorno):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM gravidade WHERE cd_transtorno = %s"
        cursor.execute(sql, (cd_transtorno,))
        bd.commit()
        #Registra log
        return jsonify({"MSG223":enviar_mensagem_positiva("MSG223"), "cd_transtorno": cd_transtorno}),201 
    except Exception as e:
        bd.rollback()
        return jsonify({"error":"Erro ao deletar gravidade: " + str(e)}),400
    finally:
        bd.close()

def deletar_gravidadePorIDTranstorno(CD_Transtorno):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM gravidade WHERE cd_transtorno = %s"
        cursor.execute(sql, (CD_Transtorno,))
        bd.commit()
        return jsonify({"MSG223":enviar_mensagem_positiva("MSG223"), "cd_transtorno": CD_Transtorno}),201 
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar gravidade: {e}"}),400
    finally:
        bd.close()