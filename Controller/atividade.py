from flask import jsonify
from Database.database import conectar_base_de_dados
from datetime import datetime, date
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Controller.log import registrar_log

tamanhos = {"nm_atividade": 100, "descricao_atividade": 2000, "dt_atividade": 12, "parecer_tecnico": 5000, "resultado": 50, "cd_meta": 9999, "cd_atividade":9999}
def formatar_data(data):
    formato = "%d-%m-%Y"
    if isinstance(data, date):
        return data.strftime("%d-%m-%Y")
    if isinstance(data, str):
        if "-" in data: 
            formato = "%d-%m-%Y"
        elif "/" in data: 
            formato = "%d/%m/%Y"
        else:
            raise ValueError(f"Formato de data inválido: {data}")
    return datetime.strptime(data, formato).strftime("%Y-%m-%d")

def carregar_atividade():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(""" SELECT
                           atv.cd_atividade,
                           atv.cd_meta,
                           atv.nm_atividade,
                           atv.descricao_atividade,
                           CAST(atv.dt_atividade AS CHAR) AS dt_atividade,
                           atv.parecer_tecnico,
                           atv.resultado,
                           atv.ativo,
                           atv.percent_conclusao
                        FROM atividade atv""")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_atividade_por_id_usuario(cd_usuario):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f""" SELECT 
                            atv.cd_atividade,
                            atv.cd_meta,
                            pm.cd_paciente,
                            up.cd_usuario,
                            atv.nm_atividade,
                            atv.descricao_atividade,
                            cast(atv.dt_atividade as CHAR) as dt_atividade,
                            atv.parecer_tecnico,
                            atv.resultado,
                            atv.ativo,
                            atv.percent_conclusao 
                        FROM atividade atv
                        LEFT JOIN paciente_meta pm
	                        ON pm.cd_meta = atv.cd_meta
                        LEFT JOIN usuario_paciente up 
	                        ON up.cd_paciente = pm.cd_paciente
                        WHERE
	                        up.cd_usuario = {cd_usuario}""")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_atividade_por_id_paciente(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"""SELECT
                            atv.cd_atividade,
                            atv.cd_meta,
                            pm.cd_paciente,
                            atv.nm_atividade,
                            atv.descricao_atividade,
                            cast(atv.dt_atividade as CHAR) as dt_atividade,
                            atv.parecer_tecnico,
                            atv.resultado,
                            atv.ativo,
                            atv.percent_conclusao
                        FROM atividade atv
                        LEFT JOIN paciente_meta pm
                            ON pm.cd_meta = atv.cd_meta
                        WHERE 
                            pm.cd_paciente = {cd_paciente}""")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_atividade_por_id_meta(cd_meta):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"""SELECT
                            atv.cd_atividade,
                            atv.cd_meta,
                            pm.cd_paciente,
                            atv.nm_atividade,
                            atv.descricao_atividade,
                            cast(atv.dt_atividade as CHAR) as dt_atividade,
                            atv.parecer_tecnico,
                            atv.resultado,
                            atv.ativo,
                            atv.percent_conclusao
                        FROM atividade atv
                        LEFT JOIN paciente_meta pm
                            ON pm.cd_meta = atv.cd_meta
                        WHERE 
                            atv.cd_meta = {cd_meta}""")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def criar_atividade(nm_atividade, descricao_atividade, dt_atividade, parecer_tecnico, resultado, cd_meta):
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
        if not cd_meta or not nm_atividade or not descricao_atividade or not dt_atividade:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        
        dt_atividade = formatar_data(dt_atividade)

        for campo, valor in list(camposG.items()):
            if valor == "" or valor == None:
                continue
            elif ((len(valor) < 5 and campo != "cd_meta") or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
            
        cursor.execute("""SELECT COUNT(*) FROM atividade WHERE nm_atividade = %s AND descricao_atividade = %s AND parecer_tecnico = %s AND cd_meta = %s AND
                    CAST(dt_atividade AS CHAR) = %s""", (camposG["nm_atividade"], camposG["descricao_atividade"], camposG["parecer_tecnico"],cd_meta, dt_atividade))
        (existe,) = cursor.fetchone()
        if existe > 0: 
            return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
#------------------FIM DAS REGRAS DE NEGÓCIO DO CREATE----------------------------------------
        sql = "INSERT INTO atividade (nm_atividade, descricao_atividade, dt_atividade, parecer_tecnico, resultado, cd_meta) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (camposG['nm_atividade'], camposG['descricao_atividade'], dt_atividade, camposG['parecer_tecnico'], resultado, cd_meta))   
        bd.commit()
        cd_atividade = cursor.lastrowid  
        #Registro de log de criação de atividade
        adicional = f"'{nm_atividade}', começo na data '{dt_atividade}' com o estado em '{resultado}'"
        ##registrar_log('CNA', meta=cd_meta, ADICIONAL=adicional)
        return jsonify({"MSG229":enviar_mensagem_positiva("MSG229"), "cd_atividade": cd_atividade}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar atividade: {e}"}), 400
    finally:
        bd.close()

def atualizar_atividade(cd_atividade,nm_atividade=None, descricao_atividade=None, dt_atividade=None, parecer_tecnico=None, resultado=None, cd_meta=None, percent_conclusao=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        if valor == None or campo in ['']:
            continue
        else:
            valor = " ".join(str(valor).split())
            valor = valor.capitalize()
            camposG[campo] = valor

    try:
        partes_sql = []
        valores = []
        if nm_atividade:
            partes_sql.append("nm_atividade = %s")
            valores.append(camposG['nm_atividade'])
        if descricao_atividade:
            partes_sql.append("descricao_atividade = %s")
            valores.append(camposG['descricao_atividade'])
        if dt_atividade:
            partes_sql.append("dt_atividade = %s")
            dt_atividade = formatar_data(dt_atividade)
            valores.append(dt_atividade)
        if parecer_tecnico:
            partes_sql.append("parecer_tecnico = %s")
            valores.append(camposG['parecer_tecnico'])
        if resultado:
            partes_sql.append("resultado = %s")
            valores.append(resultado)
        if cd_meta:
            partes_sql.append("cd_meta = %s")
            valores.append(cd_meta)
        if percent_conclusao:
            partes_sql.append("percent_conclusao = %s")
            valores.append(percent_conclusao)

        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204")}),204
        
#-----------------------------COMEÇO DAS RNs DO UPDATE----------------------------------------
        if not nm_atividade or not descricao_atividade or not dt_atividade:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
    
        
        cursor.execute("""SELECT COUNT(*) FROM atividade WHERE nm_atividade = %s AND descricao_atividade = %s AND parecer_tecnico = %s AND cd_meta = %s AND cd_atividade != %s""",
                    (camposG["nm_atividade"], camposG["descricao_atividade"], camposG["parecer_tecnico"],cd_meta, cd_atividade))
        (existe,) = cursor.fetchone()
        if existe > 0: 
            return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
#-----------------------------FIM DAS RNs DO UPDATE-------------------------------------------
        sql = f"UPDATE atividade SET {', '.join(partes_sql)} WHERE cd_atividade = {cd_atividade}"
        cursor.execute(sql, tuple(valores))
        bd.commit()
        #registro do log de alteração
        adicional = f"{nm_atividade}, com {percent_conclusao}% de conclusão e estado {resultado}"
        ##registrar_log('ADA', meta=cd_meta, ADICIONAL=adicional)
        return jsonify({"MSG230":enviar_mensagem_positiva("MSG230"), "cd_atividade": cd_atividade}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao atualizar atividade: {e}"}),400
    finally:
        bd.close()

def deletar_atividade(cd_atividade):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        #SELECT PARA PEGAR OS DADOS DA meta PARA O LOG
        #cursor.execute("SELECT cd_meta, nm_atividade from atividade WHERE cd_atividade = %s", (cd_atividade,))
        sql = "DELETE FROM atividade WHERE cd_atividade = %s"
        cursor.execute(sql, (cd_atividade,))
        bd.commit()
        return jsonify({"MSG261": enviar_mensagem_positiva("MSG261")}),201
    except Exception as e:
        bd.rollback()   
        return jsonify({"error": f"Erro ao deletar atividade: {e}"})
    finally:
        bd.close()

def inativar_atividade(cd_atividade):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT ativo FROM atividade WHERE cd_atividade = %s", (cd_atividade,)),201
        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({"Success":f"Atividade com código {cd_atividade} não encontrada!"}),204

        estado_atual = resultado[0]
        novo_estado = 'N' if estado_atual == 'S' else 'S'
        if estado_atual == 'S':
            novo_estado = 'N'
            novo_resultado = 'Concluído'
        else:
            novo_estado = 'S'
            novo_resultado = 'Em andamento'
            
        cursor.execute("UPDATE atividade SET ativo = %s, resultado = %s WHERE cd_atividade = %s", 
                      (novo_estado, novo_resultado, cd_atividade))
        bd.commit()
        cursor.execute("SELECT cd_meta, nm_atividade from atividade WHERE cd_atividade = %s", (cd_atividade,))
        (cd_meta, nm_atividade) = cursor.fetchone()
        if novo_estado == "N":
            adicional = f"'{nm_atividade}' alterado para inativa"
            #registrar_log('AEA', meta=cd_meta, ADICIONAL=adicional)
            return jsonify({"MSG231":enviar_mensagem_positiva("MSG231")}),201
        elif novo_estado == "S":
            adicional = f"'{nm_atividade}' alterado para ativa"
            #registrar_log('AEA', meta=cd_meta, ADICIONAL=adicional)
            return jsonify({"MSG232":enviar_mensagem_positiva("MSG232")}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao alterar estado da atividade: {e}"}),400

    finally:
        bd.close()