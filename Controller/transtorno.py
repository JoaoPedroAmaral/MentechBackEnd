from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_positiva, enviar_mensagem_negativa
from Database.database import load_dotenv
import os
load_dotenv()
senha = os.getenv("CRIPT_PASSWORD")
tamanhos = {'nm_transtorno': 100, 'apoio_diag': 3000, 'prevalencia': 1000, 'fatores_risco_prognostico': 30000, 'diagnostico_genero': 1000}

def carregar_transtorno():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""SELECT t.cd_transtorno,
                    CAST(AES_DECRYPT(t.nm_transtorno, %s) AS CHAR) AS nm_transtorno,
                    CAST(AES_DECRYPT(c.cid11, %s) AS CHAR) AS cid11,
                    t.apoio_diag,
                    t.prevalencia,
                    t.fatores_risco_prognostico,
                    t.diagnostico_genero FROM transtorno t LEFT JOIN cid11 c ON c.cd_cid = t.cd_cid""", (senha, senha))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_transtorno_PorIdTranstorno(id):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""SELECT t.cd_transtorno,
                    CAST(AES_DECRYPT(t.nm_transtorno, %s) AS CHAR) AS nm_transtorno,
                    CAST(AES_DECRYPT(c.cid11, %s) AS CHAR) AS cid11,
                    t.apoio_diag,
                    t.prevalencia,
                    t.fatores_risco_prognostico,
                    t.diagnostico_genero 
                    FROM transtorno t LEFT JOIN cid11 c ON c.cd_cid = t.cd_cid 
                    WHERE cd_transtorno = %s""", (senha, senha, id))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def criar_transtorno(nm_transtorno, cid11, apoio_diag, prevalencia, fatores_risco_prognostico, diagnostico_genero):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        if valor == None:
            continue
        elif campo != "cid11":
            valor = " ".join(str(valor).split())
            valor = valor.capitalize()
            camposG[campo] = valor
        else:
            valor = " ".join(str(valor).split())
            camposG[campo] = valor
            
    try:
#--------------------COMEÇO DAS RNs DO CREATE-----------------------------------
        if not nm_transtorno or not cid11:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        for campo, valor in list(camposG.items()):
            if valor == "" or valor == None or campo not in tamanhos.keys():
                continue
            elif ((len(valor) < 4) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400  
             
        cursor.execute("SELECT CAST(AES_DECRYPT(nm_transtorno, %s) AS CHAR) AS nm_transtorno, CAST(AES_DECRYPT(c.cid11, %s) as CHAR) AS cid11 FROM transtorno t LEFT JOIN cid11 c ON c.cd_cid = t.cd_cid", (senha, senha))
        transtornos = cursor.fetchall()
        for nome, cid in transtornos:
            if nome == camposG['nm_transtorno'] or cid == camposG['cid11']:
                return jsonify({"MSG201":enviar_mensagem_negativa("MSG201")}),400
#------------------FIM DAS REGRAS DE NEGÓCIO DO CREATE----------------------------------------
        cursor.execute("INSERT INTO cid11 (cid11) VALUES(AES_ENCRYPT(%s, %s))", (camposG['cid11'], senha))
        cd_cid = cursor.lastrowid
        sql = "INSERT INTO transtorno (nm_transtorno, cd_cid, apoio_diag, prevalencia, fatores_risco_prognostico, diagnostico_genero) VALUES (AES_ENCRYPT(%s, %s), %s, %s, %s, %s, %s)"
        cursor.execute(sql,(camposG['nm_transtorno'], senha, cd_cid, camposG['apoio_diag'], camposG['prevalencia'], camposG['fatores_risco_prognostico'], camposG['diagnostico_genero']))
        cd_transtorno = cursor.lastrowid  
        bd.commit()
        return jsonify({"MSG036":enviar_mensagem_positiva("MSG036"), "cd_transtorno": cd_transtorno}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"Erro ao adicionar Transtorno. Tente novamente": str(e)}),500
    finally:
        bd.close()


def atualizar_transtorno(cd_transtorno, nm_transtorno=None, cid11=None, apoio_diag=None, prevalencia=None, fatores_risco_prognostico=None, diagnostico_genero=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        if valor == None:
            continue
        elif campo != "cid11":
            valor = " ".join(str(valor).split())
            valor = valor.capitalize()
            camposG[campo] = valor
        else:
            valor = " ".join(str(valor).split())
            camposG[campo] = valor
    try:
        partes_sql = []
        valores = []
        campos = []

        if nm_transtorno:
            partes_sql.append("nm_transtorno = AES_ENCRYPT(%s, %s)")
            valores.append(camposG['nm_transtorno'])
            valores.append(senha)
            campos.append(f"CAST(AES_DECRYPT(nm_transtorno, '{senha}') AS CHAR) AS nm_transtorno")
        if cid11:
            partes_sql.append("cd_cid = %s")
            cursor.execute(f"SELECT cd_cid from transtorno WHERE cd_transtorno = {cd_transtorno}")
            (cd_cid,) = cursor.fetchone()
            cursor.execute("SELECT CAST(AES_DECRYPT(cid11, %s) AS CHAR) AS cid11 from cid11 WHERE cd_cid = %s", (senha, cd_cid))
            (cid,) = cursor.fetchone()
            valores.append(cd_cid)
        if apoio_diag:
            partes_sql.append("apoio_diag = %s")
            valores.append(camposG['apoio_diag'])
            campos.append("apoio_diag")
        if prevalencia:
            partes_sql.append("prevalencia = %s")
            valores.append(camposG['prevalencia'])
            campos.append("prevalencia")
        if fatores_risco_prognostico:
            partes_sql.append("fatores_risco_prognostico = %s")
            valores.append(camposG['fatores_risco_prognostico'])
            campos.append("fatores_risco_prognostico")
        if diagnostico_genero:
            partes_sql.append("diagnostico_genero = %s")
            valores.append(camposG['diagnostico_genero'])
            campos.append("diagnostico_genero")

        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204")}),204
        
#-----------------------------COMEÇO DAS RNs DO UPDATE----------------------------------------
        for campo, valor in list(camposG.items())[1:]:
            if valor == "" or valor == None or campo not in tamanhos.keys():
                continue
            elif((len(valor) < 4) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
        #PEGA VALORES DOS OUTROS REGISTROS NA TABELA E ARMAZENA NA VARIAVEL "campos_resultado"
        valores.append(cd_transtorno)
        campos.append("cd_transtorno")
        sql_verificacao = f"SELECT {', '.join(campos)} FROM transtorno"
        cursor.execute(sql_verificacao)
        campos_resultado = cursor.fetchall()
        #VERIFICA SE É DUPLICADO, SE FOR APRESENTA ERRO SE NÃO, CONTINUA
        for transtorno in campos_resultado:
            transtorno = list(transtorno)
            if all(valor in transtorno[:-1] for valor in valores[2:-1]) and valores[-1] != transtorno[-1] and camposG["cid11"] == cid:
                return jsonify({"MSG211":enviar_mensagem_negativa("MSG211")}),400
            elif transtorno[0] == valores[0] and camposG["cid11"] == cid and valores[-1] != transtorno[-1]:
                return jsonify({"MSG201":enviar_mensagem_negativa("MSG201")}),400
            else:
                continue
        #VERIFICAÇÃO SE O cid11 JÁ EXISTE
        cursor.execute("SELECT COUNT(cid11) from cid11 WHERE cid11 = AES_ENCRYPT(%s, %s) AND cd_cid != %s", (camposG["cid11"], senha, cd_cid))
        (existe, ) = cursor.fetchone()
        if existe > 0:
            return jsonify({"MSG201":enviar_mensagem_negativa("MSG201")}),400 
#-----------------------------FIM DAS RNs DO UPDATE-------------------------------------------
        cursor.execute("UPDATE cid11 SET cid11 = AES_ENCRYPT(%s, %s) WHERE cd_cid = %s", (camposG["cid11"], senha, cd_cid))
        sql = f"UPDATE transtorno SET {', '.join(partes_sql)} WHERE cd_transtorno = %s"
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return jsonify({"MSG037":enviar_mensagem_positiva("MSG037"), "cd_transtorno": cd_transtorno}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao editar o transtorno: {e}. Tente novamente."}),400
    finally:
        bd.close()

def deletar_transtorno(cd_transtorno):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM transtorno WHERE cd_transtorno = %s"
        cursor.execute(sql, (cd_transtorno,))
        bd.commit()
        return jsonify({"MSG038":enviar_mensagem_positiva("MSG038"), "cd_transtorno": cd_transtorno}),200

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"“Erro ao remover transtorno: {e}. Tente novamente."}),400
    finally:
        bd.close()