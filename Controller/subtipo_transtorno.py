from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Database.database import load_dotenv
import os
load_dotenv()
senha = os.getenv("CRIPT_PASSWORD")

tamanhos = {"nm_subtipo":500, "obs":2000, "cid11": 7, 'cd_transtorno': 9999}

def carregar_subtipo_transtorno():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""
                   SELECT
                        cd_subtipo,
                        cd_transtorno,
                        CAST(AES_DECRYPT(nm_subtipo, %s) AS CHAR) AS nm_subtipo,
                        CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11,
                        obs 
                   FROM subtipo_transtorno st
                   left join cid11 cid on cid.cd_cid = st.cd_cid""", (senha,senha))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_subtipo_transtorno_PorIdTranstorno(id):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""
                   SELECT
                        cd_subtipo,
                        cd_transtorno,
                        CAST(AES_DECRYPT(nm_subtipo, %s) AS CHAR) AS nm_subtipo,
                        CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11,
                        obs 
                   FROM subtipo_transtorno st
                   left join cid11 cid on cid.cd_cid = st.cd_cid
                   WHERE cd_transtorno = %s""", (senha, senha, id))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_subtipo_transtorno_PorIdSubtipo(id):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""
                   SELECT
                        cd_subtipo,
                        cd_transtorno,
                        CAST(AES_DECRYPT(nm_subtipo, %s) AS CHAR) AS nm_subtipo,
                        CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11,
                        obs 
                   FROM subtipo_transtorno st
                   left join cid11 cid on cid.cd_cid = st.cd_cid
                   WHERE cd_subtipo = %s""", (senha, senha, id))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def criar_subtipo_transtorno(nm_subtipo, cid11, obs, cd_transtorno):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        if valor == None or campo in ("cid11", "cd_transtorno"):    
            continue
        else:
            valor = " ".join(str(valor).split())
            valor = valor.capitalize()
            camposG[campo] = valor
    try:
#-------------------------COMEÇO DAS RNs DO CREATE--------------------------------------------
        if any(valor in ("", None, '') for valor in list(camposG.values())[:-1]):
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        for campo, valor in list(camposG.items())[:-1]:#[:-1] para n pegar o cd_transtorno
            if valor in ("", None, '') or campo in ('cd_transtorno'):
                continue
            elif ((len(valor) < 4) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
                                 
        cursor.execute("SELECT CAST(AES_DECRYPT(nm_subtipo, %s) AS CHAR), cid11 FROM subtipo_transtorno st left join cid11 cid on cid.cd_cid = st.cd_cid", (senha,))
        subtipos = cursor.fetchall()
        for nome, cid in subtipos:  
            if nome == camposG['nm_subtipo'] or cid == camposG['cid11']:  
                return jsonify({"MSG201":enviar_mensagem_negativa("MSG201")}),400
#--------------------------FIM DAS RNs DO CREATE----------------------------------------------
        cursor.execute("INSERT INTO cid11 (cid11) VALUES (AES_ENCRYPT(%s, %s))", (cid11, senha))
        cd_cid = cursor.lastrowid
        sql = "INSERT INTO subtipo_transtorno (nm_subtipo, cd_cid, obs, cd_transtorno) VALUES (AES_ENCRYPT(%s, %s), %s, %s, %s)"
        cursor.execute(sql, (camposG['nm_subtipo'], senha, cd_cid, camposG['obs'], camposG['cd_transtorno']))
        bd.commit()
        cd_subtipo = cursor.lastrowid
        return jsonify({"MSG206":enviar_mensagem_positiva("MSG206"), "cd_subtipo": cd_subtipo}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao adicionar o Subtipo: {e}."}),400
    finally:
        bd.close()

def atualizar_subtipo_transtorno(cd_subtipo,nm_subtipo=None, cid11=None, obs=None, cd_transtorno=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        if valor == None or campo in ('cid11', "cd_transtorno"):
            continue
        else:
            valor = " ".join(str(valor).split())
            valor = valor.capitalize()
            camposG[campo] = valor
    try:
        partes_sql = []
        valores = []
        campos = []
        
        if nm_subtipo:
            partes_sql.append("nm_subtipo = AES_ENCRYPT(%s, %s)")
            valores.append(camposG['nm_subtipo'])
            valores.append(senha)
            campos.append(f"CAST(AES_DECRYPT(nm_subtipo, '{senha}') AS CHAR) AS nm_subtipo")
        if cid11:
            partes_sql.append("cd_cid = %s")
            cursor.execute(f"SELECT cd_cid from subtipo_transtorno WHERE cd_subtipo = {cd_subtipo}")
            (cd_cid,) = cursor.fetchone()
            cursor.execute("SELECT CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11 from cid11 WHERE cd_cid = %s", (senha, cd_cid))
            (cid,) = cursor.fetchone()
            valores.append(cd_cid)
        if obs:
            partes_sql.append("obs = %s")
            valores.append(camposG['obs'])
            campos.append("obs")
        if cd_transtorno:
            partes_sql.append("cd_transtorno = %s")
            valores.append(camposG['cd_transtorno'])
            
        valores.append(camposG['cd_subtipo'])

        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204"), "cd_subtipo":cd_subtipo}),400
#-----------------------------COMEÇO DAS RNs DO UPDATE----------------------------------------
        
        for campo, valor in list(camposG.items()):
            if valor == "" or valor == None or campo in ['cd_transtorno', 'cd_subtipo']:
                continue
            elif ((len(valor) < 4) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
             
        #PEGA VALORES DOS OUTROS REGISTROS NA TABELA E ARMAZENA NA VARIAVEL "campos_resultado"
        campos.append("CAST(cd_subtipo AS CHAR)")
        sql_verificacao = f"SELECT {', '.join(campos)} FROM subtipo_transtorno WHERE cd_transtorno = {cd_transtorno}"
        cursor.execute(sql_verificacao)
        campos_resultado = cursor.fetchall()
        #VERIFICA SE É DUPLICADO, SE FOR APRESENTA ERRO SE NÃO, CONTINUA
        for subtipo in campos_resultado:
            subtipo = list(subtipo)
            if all(valor in valores for valor in subtipo):
                return jsonify({"MSG202":enviar_mensagem_negativa("MSG202")}),400
            elif subtipo[1] == valores[2] and valores[-1] != subtipo[-1]:
                return jsonify({"MSG203":enviar_mensagem_negativa("MSG203")}),400
            else:
                continue            
#-----------------------------FIM DAS RNs DO UPDATE-------------------------------------------        
        sql = f"UPDATE subtipo_transtorno SET {', '.join(partes_sql)} WHERE cd_subtipo = %s"
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return jsonify({"MSG207": enviar_mensagem_positiva("MSG207"), "cd_subtipo": cd_subtipo}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao editar Subtipo: {e}"}),400
    finally:
        bd.close()

def deletar_subtipo_transtorno(cd_subtipo):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM subtipo_transtorno WHERE cd_subtipo = %s"
        cursor.execute(sql, (cd_subtipo,))
        bd.commit()
        return jsonify({"MSG208":enviar_mensagem_positiva("MSG208"), "cd_subtipo": cd_subtipo}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao remover Subtipo: {e}"}),400

    finally:
        bd.close()

def deletar_subtipoPorIdTranstorno(cd_transtorno):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM subtipo_transtorno WHERE cd_transtorno = %s"
        cursor.execute(sql, (cd_transtorno,))
        bd.commit()
        return ({"MSG209":enviar_mensagem_positiva("MSG209"), "cd_transtorno": cd_transtorno}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao remover Subtipos: {e}"}),400

    finally:
        bd.close()