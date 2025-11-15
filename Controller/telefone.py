from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva

tamanhos = {'ddd': 2, 'nr_telefone': 9}
def carregar_telefone():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT * FROM telefone")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_telefone_por_id_paciente(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    sql = "SELECT * FROM telefone WHERE cd_paciente = %s"
    cursor.execute(sql, (cd_paciente,))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_telefone_por_id_responsavel(cd_responsavel):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    sql = "SELECT * FROM telefone WHERE cd_responsavel = %s"
    cursor.execute(sql, (cd_responsavel,))
    linhas = cursor.fetchall()
    bd.close()
    return linhas


def criar_telefone(ddd, nr_telefone, tipo, cd_paciente, cd_responsavel):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
#--------------------COMEÇO DAS RNs DO CREATE-------------------------------------------------
        if not ddd or not nr_telefone:
            return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}),400
        
        if (len(str(ddd)) < 2 or len(str(ddd)) > tamanhos['ddd']) or (len(str(nr_telefone)) < 8 or len(str(nr_telefone)) > tamanhos["nr_telefone"]):
            return jsonify({"MSG199": enviar_mensagem_negativa("MSG199")}),400
            
        sql_verifica = """
            SELECT COUNT(*) FROM telefone 
            WHERE ddd = %s AND nr_telefone = %s 
              AND (cd_paciente = %s OR cd_responsavel = %s)
        """
        cursor.execute(sql_verifica, (ddd, nr_telefone, cd_paciente, cd_responsavel))
        (resultado, ) = cursor.fetchone()
        
        if resultado >= 1:            
            return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
#------------------FIM DAS REGRAS DE NEGÓCIO DO CREATE----------------------------------------
        
        sql = "INSERT INTO telefone (ddd, nr_telefone, tipo, cd_paciente, cd_responsavel) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (ddd, nr_telefone, tipo ,cd_paciente, cd_responsavel))
        bd.commit()
        return jsonify({"MSG210": enviar_mensagem_positiva("MSG210")}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao criar telefone: {e}"}),400
    finally:
        bd.close()

def atualizar_telefone(cd_telefone, ddd=None, tipo=None, nr_telefone=None, cd_paciente=None, cd_responsavel=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    try:
        #partes_sql: USADO PARA ARMAZENAR OS CAMPOS PARA MONTAR O UPDATE
        partes_sql = []
        #values: USADO PARA ARMAZENAR OS VALORES DO UPDATE
        valores = []
        #campos: USADO PARA ARMAZENAR OS CAMPOS, PK E EVENTUALEMNTE VALORES PARA A VERIFICACAO DE DUPLICIDADE
        campos = []
        
        if ddd:
            partes_sql.append("ddd = %s")
            valores.append(ddd)
            campos.append("ddd")
        if tipo:
            partes_sql.append("tipo = %s")
            valores.append(tipo)
            campos.append("tipo")
        if nr_telefone:
            partes_sql.append("nr_telefone = %s")
            valores.append(nr_telefone)
            campos.append("nr_telefone")
        if cd_paciente:
            partes_sql.append("cd_paciente = %s")
            valores.append(cd_paciente)
            campos.append("cd_paciente")
        if cd_responsavel:
            partes_sql.append("cd_responsavel = %s")
            valores.append(cd_responsavel)
            campos.append("cd_responsavel")

        if not partes_sql:
            return ({"MSG204": enviar_mensagem_negativa("MSG204")}),400
        
#-----------------------------COMEÇO DAS RNs DO UPDATE----------------------------------------
        if (len(str(nr_telefone)) < 4) or (len(str(nr_telefone)) > tamanhos["nr_telefone"]):
            return jsonify({"MSG199": enviar_mensagem_negativa("MSG199")}),400
        
        if len(str(ddd)) < 2 or len(str(ddd)) > 2:
            return jsonify({"MSG199": enviar_mensagem_negativa("MSG199")}),400
            

        #PEGA VALORES DOS OUTROS REGISTROS NA TABELA E ARMAZENA NA VARIAVEL "campos_resultado"
        valores.append(cd_telefone)
        campos.append("cd_telefone")
        sql_verificacao = f"SELECT {', '.join(campos)} FROM telefone"
        cursor.execute(sql_verificacao)
        campos_resultado = cursor.fetchall()
        
        #VERIFICA SE É DUPLICADO, SE FOR APRESENTA ERRO SE NÃO, CONTINUA
        for telefone in campos_resultado:
            telefone = list(telefone)
            if all(valor in telefone[:-1] for valor in valores[:-1]) and valores[-1] != telefone[-1]:
                return jsonify({"MSG202": enviar_mensagem_negativa("MSG202")}),400
            else:
                continue
#-----------------------------FIM DAS RNs DO UPDATE-------------------------------------------
        sql = f"UPDATE telefone SET {', '.join(partes_sql)} WHERE cd_telefone = %s"
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return jsonify({"MSG212": enviar_mensagem_positiva("MSG212")}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao atualizar o telefone: {e}"}),400
    finally:
        bd.close()

def deletar_telefone(cd_telefone):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM telefone WHERE cd_paciente = %s"
        cursor.execute(sql, (cd_telefone,))
        bd.commit()
        return jsonify({"MSG213": enviar_mensagem_positiva("MSG213")}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar telefone: {e}"}),400

    finally:
        bd.close()