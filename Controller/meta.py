from flask import jsonify
from Database.database import conectar_base_de_dados
from datetime import datetime, date
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Controller.log import registrar_log

tamanhos = {'meta': 100, 'obs_meta': 500}

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

def carregar_meta():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"SELECT cd_meta, CAST(dt_cadastro AS CHAR) AS dt_cadastro, meta, obs_meta, ativo from meta")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_meta_PorPaciente(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"SELECT m.cd_meta, CAST(m.dt_cadastro AS CHAR) AS dt_cadastro, m.meta, m.obs_meta, m.ativo, CAST(pm.dt_previsao AS CHAR) AS dt_previsao, CAST(pm.dt_conclusao AS CHAR) AS dt_conclusao, pm.cd_paciente FROM meta m LEFT JOIN paciente_meta pm ON pm.cd_meta = m.cd_meta WHERE pm.cd_paciente = {cd_paciente}")
    linhas = cursor.fetchall()
    bd.close()
    return linhas


def criar_meta(meta, obs_meta):
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
        hoje = formatar_data(datetime.today().strftime('%d-%m-%Y'))
           
        cursor.execute("SELECT COUNT(*) FROM meta WHERE meta = %s AND obs_meta = %s", (camposG['meta'], camposG['obs_meta']))
        (existe,) = cursor.fetchone()
        if existe > 0: return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
        
        
        
        if not obs_meta or not meta:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        for campo, valor in list(camposG.items()):
            if valor == "" or valor == None:
                continue
            elif ((len(valor) < 3) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
#------------------FIM DAS REGRAS DE NEGÓCIO DO CREATE----------------------------------------      
        sql = "INSERT INTO meta (dt_cadastro, meta, obs_meta) VALUES (%s, %s, %s)"
        cursor.execute(sql, (hoje, meta, obs_meta))
        cd_meta = cursor.lastrowid
        bd.commit()
        #Registra log
        adicional = f"'{camposG['meta']}', '{camposG['obs_meta']}'"
        #registrar_log('CMT', meta=cd_meta, ADICIONAL=adicional)
        return jsonify({"MSG194":enviar_mensagem_positiva("MSG194"), "cd_meta": cd_meta}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar a meta: {e}"}),400
    finally:
        bd.close()

"""def atualizar_meta(ID_META,cd_paciente=None, dt_cadastro=None, meta=None, obs_meta=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        partes_sql = []
        valores = []
        if cd_paciente:
            partes_sql.append("cd_paciente = %s")
            valores.append(cd_paciente)
        if dt_cadastro:
            dt_cadastro = formatar_data(dt_cadastro)
            partes_sql.append("dt_cadastro = %s")
            valores.append(dt_cadastro)
        if meta:
            partes_sql.append("meta = %s")
            valores.append(meta)
        if obs_meta:
            partes_sql.append("obs_meta = %s")
            valores.append(obs_meta)

        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204"), "cd_paciente":cd_paciente}),400


        sql = f"UPDATE meta SET {', '.join(partes_sql)} WHERE ID_META = %s"
        valores.append(ID_META)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        print("Meta atualizada com sucesso!")
    except Exception as e:
        bd.rollback()
        print(f"Erro ao atualizar a meta: {e}")
    finally:
        bd.close()"""

def remover_meta(cd_meta):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT meta, obs_meta FROM meta WHERE cd_meta = %s",(cd_meta,))
        meta, obs_meta = cursor.fetchone()
        sql = "DELETE FROM meta WHERE cd_meta = %s"
        cursor.execute(sql, (cd_meta,))
        bd.commit()
        adicional = f"'{meta}', '{obs_meta}'"
        #registrar_log('RMT', meta=cd_meta, ADICIONAL=adicional)
        return jsonify({"MSG197": enviar_mensagem_positiva("MSG197"), "cd_meta": cd_meta}),200
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao deletar a meta: {e}"})
    finally:
        bd.close()

def inativar_meta(cd_meta):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT ativo FROM meta WHERE cd_meta = %s", (cd_meta,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"Success",f"meta com código {cd_meta} não encontrada!"}),204

        estado_atual = result[0]
        novo_estado = 'N' if estado_atual == 'S' else 'S'

        cursor.execute("UPDATE meta SET ativo = %s WHERE cd_meta = %s", (novo_estado, cd_meta))
        bd.commit()
        
        cursor.execute("SELECT meta from meta WHERE cd_meta = %s", (cd_meta,))
        (meta,) = cursor.fetchone()
        if novo_estado == "N":
            adicional = f"'{meta}' alterado para inativa"
            #registrar_log('AEMT', meta=cd_meta, ADICIONAL=adicional)
            return jsonify({"MSG233":enviar_mensagem_positiva("MSG233")}),201
        elif novo_estado == "S":
            adicional = f"'{meta}' alterado para ativa"
            #registrar_log('AEMT', meta=cd_meta, ADICIONAL=adicional)
            return jsonify({"MSG234":enviar_mensagem_positiva("MSG234")}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao alterar estado da atividade: {e}"}),400

    finally:
        bd.close()