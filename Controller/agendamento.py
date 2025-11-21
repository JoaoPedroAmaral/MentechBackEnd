from flask import jsonify
from Database.database import conectar_base_de_dados
from datetime import datetime, date, timedelta
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Controller.log import registrar_log

def formatar_data(data):
    formato = "%d-%m-%Y"
    if isinstance(data, date):
        return data.strftime("%Y-%m-%d")
    if isinstance(data, str):
        if "-" in data: 
            formato = "%d-%m-%Y"
        elif "/" in data: 
            formato = "%d/%m/%Y"
        else:
            raise ValueError(f"Formato de data inválido: {data}")
    return datetime.strptime(data, formato).strftime("%Y-%m-%d")

def carregar_agendamentos():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""SELECT cd_agendamento, 
                   cd_usuario, 
                   cd_paciente, 
                   CAST(dt_agendamento AS CHAR) AS dt_agendamento,
                   CAST(hora_inicio AS CHAR) AS hora_inicio,
                   CAST(hora_fim AS CHAR) AS hora_fim FROM agendamento""")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_agendamentos_por_id_usuario(cd_usuario):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"""SELECT cd_agendamento, 
                   cd_usuario, 
                   cd_paciente, 
                   CAST(dt_agendamento AS CHAR) AS dt_agendamento,
                   CAST(hora_inicio AS CHAR) AS hora_inicio,
                   CAST(hora_fim AS CHAR) AS hora_fim 
                   FROM agendamento WHERE cd_usuario = {cd_usuario}""")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_agendamentos_por_id_paciente(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"""SELECT cd_agendamento, 
                   cd_usuario, 
                   cd_paciente, 
                   CAST(dt_agendamento AS CHAR) AS dt_agendamento,
                   CAST(hora_inicio AS CHAR) AS hora_inicio,
                   CAST(hora_fim AS CHAR) AS hora_fim 
                   FROM agendamento WHERE cd_paciente = {cd_paciente}""")
    linhas = cursor.fetchall()
    bd.close()
    return linhas    

def criar_agendamento(cd_usuario, cd_paciente, dt_agendamento, hora_inicio, hora_fim, prazo):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    prazos = {"": 1, "1_mes": 4, "6_meses": 24, "1_ano": 48}
    agendamentos = []
    try:
        if not cd_usuario or not cd_paciente or not dt_agendamento or not hora_inicio:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        for i in range (prazos[prazo]):
            dt_agendamento = datetime.strptime(dt_agendamento, "%Y-%m-%d")
            if i >= 1:
                dt_agendamento += timedelta(days=7)  
                hora_inicio = hora_inicio.strftime("%H:%M:%S")
                hora_fim = hora_fim.strftime("%H:%M:%S")  
            hora_inicio = datetime.strptime(hora_inicio, "%H:%M:%S").time()
            hora_fim = datetime.strptime(hora_fim, "%H:%M:%S").time()
            hoje = datetime.strptime(formatar_data(datetime.today()), '%Y-%m-%d')

            if dt_agendamento < hoje:
                return jsonify({"MSG260": enviar_mensagem_negativa("MSG260")}),400
            
    #--------------------COMEÇO DAS RNs DO CREATE-------------------------------------------------
            dt_agendamento = formatar_data(dt_agendamento)
            cursor.execute(f"SELECT CAST(hora_inicio AS CHAR) AS hora_inicio, CAST(hora_fim AS CHAR) AS hora_fim FROM agendamento WHERE dt_agendamento = '{dt_agendamento}' and cd_usuario = {cd_usuario}")
            horarios = cursor.fetchall()
            if hora_inicio >= hora_fim:
                return jsonify({"MSG248": enviar_mensagem_negativa("MSG248")}),401
            for hora_ini, hora_f in horarios:
                hora_ini = datetime.strptime(hora_ini, "%H:%M:%S").time()
                hora_f = datetime.strptime(hora_f, "%H:%M:%S").time()
                if hora_inicio >= hora_fim:
                    return jsonify({"MSG248": enviar_mensagem_negativa("MSG248")}),401
                if (hora_ini <= hora_inicio <= hora_f) or (hora_inicio == hora_f) or (hora_inicio == hora_ini):
                    return jsonify({"MSG248": enviar_mensagem_negativa("MSG248")}),401
                elif (hora_ini <= hora_fim <= hora_f) or (hora_fim == hora_f) or (hora_fim == hora_ini):
                    return jsonify({"MSG249": enviar_mensagem_negativa("MSG249")}),401 
    #------------------FIM DAS REGRAS DE NEGÓCIO DO CREATE----------------------------------------
            sql = "INSERT INTO agendamento(cd_usuario, cd_paciente, dt_agendamento, hora_inicio, hora_fim, comparecimento) VALUES (%s, %s, %s, %s, %s, 'N')"
            cursor.execute(sql, (cd_usuario, cd_paciente, dt_agendamento, hora_inicio, hora_fim))
            cd_agendamento = cursor.lastrowid
            agendamentos.append(cd_agendamento)     
            bd.commit()
            #cursor.execute("SELECT nm_paciente FROM paciente WHERE cd_paciente = %s", (cd_paciente,))
            #(nm_paciente,) = cursor.fetchone()
            #adicional = f"Dia {dt_agendamento}, das {hora_inicio} até as {hora_fim} para o paciente {nm_paciente}"
            #registrar_log('CAG', cd_paciente=cd_paciente, ADICIONAL=adicional)
            print("tipo_no_final",type(dt_agendamento))
        return jsonify({"MSG246":enviar_mensagem_positiva("MSG246"), "cd_agendamento(s)": agendamentos}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar agendamento: {e}"}), 400
    finally:
        bd.close()
        
def atualizar_agendamento(cd_agendamento, cd_usuario, cd_paciente, dt_agendamento=None, hora_inicio=None, hora_fim=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        partes_sql = []
        valores = []
        if dt_agendamento:
            dt_agendamento = formatar_data(dt_agendamento)
            partes_sql.append("dt_agendamento = %s")
            valores.append(dt_agendamento)
        if hora_inicio:
            hora_inicio = datetime.strptime(hora_inicio, "%H:%M:%S").time()
            partes_sql.append("hora_inicio = %s")
            valores.append(hora_inicio)
        if hora_fim:
            hora_fim = datetime.strptime(hora_fim, "%H:%M:%S").time()
            partes_sql.append("hora_fim = %s")
            valores.append(hora_fim)
        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204")}),204
        
#-----------------------------COMEÇO DAS RNs DO UPDATE----------------------------------------
        hoje = formatar_data(datetime.today().strftime('%d-%m-%Y'))
        
        if not dt_agendamento or not hora_inicio or not hora_fim:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        
        if dt_agendamento < hoje:
            return jsonify({"MSG260": enviar_mensagem_negativa("MSG260")}),400
    
        cursor.execute(f"SELECT CAST(hora_inicio AS CHAR) AS hora_inicio, CAST(hora_fim AS CHAR) AS hora_fim FROM agendamento WHERE dt_agendamento = '{dt_agendamento}' and cd_usuario = {cd_usuario} and cd_agendamento != {cd_agendamento}")
        horarios = cursor.fetchall()
        if hora_inicio >= hora_fim:
            return jsonify({"MSG248": enviar_mensagem_negativa("MSG248")}),401
        for hora_ini, hora_f in horarios:
            hora_ini = datetime.strptime(hora_ini, "%H:%M:%S").time()
            hora_f = datetime.strptime(hora_f, "%H:%M:%S").time()
            if (hora_ini <= hora_inicio <= hora_f) or (hora_inicio == hora_f) or (hora_inicio == hora_ini):
                return jsonify({"MSG248": enviar_mensagem_negativa("MSG248")}),401
            elif (hora_ini <= hora_fim <= hora_f) or (hora_fim == hora_f) or (hora_fim == hora_ini):
                return jsonify({"MSG249": enviar_mensagem_negativa("MSG249")}),401    
#-----------------------------FIM DAS RNs DO UPDATE-------------------------------------------
        
        sql = f"UPDATE agendamento SET {', '.join(partes_sql)} WHERE cd_agendamento = {cd_agendamento}"
        cursor.execute(sql, tuple(valores))
        bd.commit()
        # cursor.execute("SELECT nm_paciente FROM paciente WHERE cd_paciente = %s", (cd_paciente,))
        # (nm_paciente, ) = cursor.fetchone()
        # adicional = f"Dia {dt_agendamento}, das {hora_inicio} até as {hora_fim} para o paciente {nm_paciente}"
        #registrar_log('ADAG', cd_paciente=cd_paciente, ADICIONAL=adicional)
        return jsonify({"MSG251":enviar_mensagem_positiva("MSG251"), "cd_agendamento": cd_agendamento}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao atualizar agendamento: {e}"}),400
    finally:
        bd.close()

def deletar_agendamento(cd_agendamento):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        # cursor.execute(f"SELECT cd_paciente, CAST(dt_agendamento AS CHAR) from agendamento WHERE cd_agendamento = {cd_agendamento}")
        # infos = cursor.fetchone()
        # cd_paciente, dt_agendamento = infos[0]
        sql = "DELETE FROM agendamento WHERE cd_agendamento = %s"
        cursor.execute(sql, (cd_agendamento,))
        bd.commit()
        #adicional = f"Data do atendimento removido {dt_agendamento}"
        #registrar_log('RAS', cd_paciente=cd_paciente, ADICIONAL=adicional)
        return jsonify({"MSG252":enviar_mensagem_positiva("MSG252"), "cd_agendamento": cd_agendamento}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"erro": f"Falha ao deletar agendamento: {e}"}), 500
    finally:
        bd.close()

def comparecimento_paciente(cd_agendamento):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT comparecimento from agendamento WHERE cd_agendamento = %s", (cd_agendamento,))
        (resultado,) = cursor.fetchone()
        if resultado == 'S':
            return jsonify({"MSG": "O status do paciente já está como comparecido!"})

        if not resultado:
            return jsonify({"Error":f"Agendamento com código {cd_agendamento} não encontrada!"}),401

        cursor.execute("UPDATE agendamento SET comparecimento = 'S' WHERE cd_agendamento = %s", (cd_agendamento,))
        bd.commit()
        # cursor.execute(f"SELECT cd_paciente, CAST(dt_agendamento AS CHAR), CAST(hora_inicio AS CHAR), CAST(hora_fim AS CHAR) from agendamento WHERE cd_agendamento = {cd_agendamento}")
        # infos = cursor.fetchone()
        # cd_paciente, dt_agendamento, hora_inicio, hora_fim = infos
        # adicional = f"Data do atendimento {dt_agendamento}, Hora de Inicio {hora_inicio}, suposto fim da sessão {hora_fim}"
        #registrar_log('CCP', cd_paciente=cd_paciente, ADICIONAL=adicional)
        return jsonify({"MSG253": enviar_mensagem_positiva("MSG253")}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao alterar estado do agendamento: {e}"}),400

    finally:
        bd.close()