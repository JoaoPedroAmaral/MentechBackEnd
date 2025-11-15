from flask import jsonify
from Database.database import conectar_base_de_dados
from datetime import datetime, date
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Controller.log import registrar_log

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

def Alternativas_por_cd_questao(cd_questao):
        bd = conectar_base_de_dados()
        cursor = bd.cursor(dictionary=True)
        cursor.execute(f"select q.cd_questao, aq.cd_alternativa, aq.alternativa from questao q left join alternativa_questao aq on aq.cd_questao = q.cd_questao where q.cd_questao = {cd_questao}")
        linhas = cursor.fetchall()
        bd.close()
        return linhas
    
def perfis():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"select p.cd_perfil, p.perfil from perfil p where p.ativo = 'S'")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_anamnese():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""select
     an.cd_anamnese,
	 pa.cd_paciente,
	 pa.nm_paciente,
     pe.cd_perfil as cd_perfil_paciente,
	 pe.perfil as perfil_do_paciente,
	 tq.tipo_questao,
     pqst.cd_perfil AS cd_perfil_questao,
	 pqst.perfil as perfil_da_questao,
	 qu.cd_questao,
	 qu.txt_questao,
	 aq.cd_alternativa,
	 aq.alternativa AS alternativa,
	 re.txt_resposta,
	 an.dt_anamnese
FROM paciente pa
	LEFT JOIN perfil pe 
		on pa.cd_perfil = pe.cd_perfil
	LEFT JOIN anamnese an 
		on an.cd_paciente = pa.cd_paciente
	left join questao_anamnese qa
		on qa.cd_anamnese = an.cd_anamnese
	LEFT JOIN resposta re 
		on re.cd_resposta = qa.cd_resposta 
	LEFT JOIN alternativa_questao aq 
		on aq.cd_alternativa = re.cd_alternativa
		and aq.cd_questao = re.cd_questao
	LEFT JOIN questao qu 
		on qu.cd_questao = qa.cd_questao
	LEFT JOIN tipo_questao tq 
		ON tq.cd_tipo_questao = qu.cd_tipo_questao
	LEFT JOIN perfil_questao pq 
		on pq.cd_questao = qu.cd_questao
	left join perfil pqst
		on pqst.cd_perfil = pq.cd_perfil
	left join agrupamento_questao aq2
		on aq2.cd_agrupamento_questao = qu.cd_questao
    ORDER BY pa.cd_paciente ASC""")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_anamnese_por_cd_paciente(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"""select
	 an.cd_anamnese,
	 pa.cd_paciente,
	 pa.nm_paciente,
     pe.cd_perfil as cd_perfil_PACIENTE,
	 pe.perfil as perfil_do_paciente,
	 tq.tipo_questao,
     pqst.cd_perfil AS cd_perfil_QUESTAO,
	 pqst.perfil as perfil_da_questao,
	 qu.cd_questao,
	 qu.txt_questao,
	 aq.cd_alternativa,
	 aq.alternativa AS alternativa,
	 re.txt_resposta,
	 an.dt_anamnese
FROM paciente pa
	LEFT JOIN perfil pe 
		on pa.cd_perfil = pe.cd_perfil
	LEFT JOIN anamnese an 
		on an.cd_paciente = pa.cd_paciente
	left join questao_anamnese qa
		on qa.cd_anamnese = an.cd_anamnese
	LEFT JOIN resposta re 
		on re.cd_resposta = qa.cd_resposta 
	LEFT JOIN alternativa_questao aq 
		on aq.cd_alternativa = re.cd_alternativa
		and aq.cd_questao = re.cd_questao
	LEFT JOIN questao qu 
		on qu.cd_questao = qa.cd_questao
	LEFT JOIN tipo_questao tq 
		ON tq.cd_tipo_questao = qu.cd_tipo_questao
	LEFT JOIN perfil_questao pq 
		on pq.cd_questao = qu.cd_questao
	left join perfil pqst
		on pqst.cd_perfil = pq.cd_perfil
	left join agrupamento_questao aq2
		on aq2.cd_agrupamento_questao = qu.cd_questao
WHERE 
	pa.cd_paciente = {cd_paciente} 
    ORDER BY pqst.cd_perfil ASC, qu.cd_questao ASC""")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def gerar_anamnese_por_perfil_do_paciente(cd_perfil, cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    cursor.execute(f"select COUNT(*) from anamnese a where a.cd_paciente = {cd_paciente}")
    (existe, ) = cursor.fetchone()
    if existe >= 1:
        return jsonify({"MSG244":enviar_mensagem_negativa("MSG244")}),400
    else:
        cursor = bd.cursor(dictionary=True)
        cursor.execute(f"""select
        q.cd_questao,
        q.txt_questao,
        q.cd_tipo_questao,
        q.obrigatorio,
        tq.tipo_questao,
        pq.cd_perfil,
        p.perfil as PERFIL_QUESTAO,
        q.cd_agrupamento_questao,
        aq.cd_agrupamento_questao,
        aq.tip_agrupamento
        from questao q 
        left join tipo_questao tq
            on tq.cd_tipo_questao = q.cd_tipo_questao
        left join perfil_questao pq
            on pq.cd_questao = q.cd_questao
        left join perfil p
            on p.cd_perfil = pq.cd_perfil
        left join agrupamento_questao aq
            on aq.cd_agrupamento_questao = q.cd_agrupamento_questao
        where
        pq.cd_perfil IN (1, {cd_perfil})
        and q.ativo = 'S' ORDER BY pq.cd_perfil ASC, q.cd_questao ASC""")
        questoes = cursor.fetchall()
        hoje = formatar_data(datetime.today().strftime('%d-%m-%Y'))
        cursor.execute("INSERT INTO anamnese (cd_paciente, dt_anamnese) VALUES (%s, %s)", (cd_paciente, hoje))
        cd_anamnese = cursor.lastrowid
        for questao in questoes:
            cursor.execute("INSERT INTO questao_anamnese (cd_anamnese, cd_questao) VALUES (%s, %s)", (cd_anamnese, questao['cd_questao']))
        bd.commit()
        cursor.execute(f"SELECT perfil FROM perfil WHERE cd_perfil = {cd_perfil}")
        perfil = cursor.fetchone()
        cursor.execute("SELECT nm_paciente FROM paciente WHERE cd_paciente = %s", (cd_paciente,))
        nm_paciente = cursor.fetchone()
        #Registra o log de Cadastro de Anamnese.
        #registrar_log('CAN', cd_paciente=cd_paciente, ADICIONAL=f'Perfil de {perfil['perfil']} para o paciente {nm_paciente['nm_paciente']}')        
        bd.close()
        return jsonify({"QUESTOES": questoes, "cd_anamnese": cd_anamnese}),201

def responder_questoes(cd_questao, cd_anamnese, cd_alternativa=None, txt_resposta=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    
    cursor.execute(f"SELECT tipo_questao FROM questao q LEFT join tipo_questao tq on tq.cd_tipo_questao = q.cd_tipo_questao WHERE q.cd_questao = {cd_questao}")
    (tipo_questao,) = cursor.fetchone()
    print(f"tipo_questao: {tipo_questao}, cd_questao: {cd_questao}, txt_questao: {txt_resposta}, cd_alternativa: {cd_alternativa}")
    if tipo_questao in ["Múltipla Escolha", "Verdadeiro ou Falso"]:
        for alternativa in cd_alternativa:
            cursor.execute("INSERT INTO resposta (cd_questao, cd_alternativa) VALUES (%s, %s)", (cd_questao, alternativa))
            cd_resposta = cursor.lastrowid
            if alternativa == cd_alternativa[0]:
                cursor.execute("UPDATE questao_anamnese SET cd_resposta = %s WHERE cd_questao = %s AND cd_anamnese = %s AND cd_resposta IS NULL", (cd_resposta, cd_questao, cd_anamnese))
            else:
                cursor.execute("INSERT INTO questao_anamnese (cd_anamnese, cd_questao, cd_resposta) VALUES (%s, %s, %s)", (cd_anamnese, cd_questao, cd_resposta))
    else:
        if txt_resposta == None:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        else:
            txt_resposta = " ".join(str(txt_resposta).split())
            cursor.execute("INSERT INTO resposta (cd_questao, txt_resposta) VALUES (%s, %s)", (cd_questao, txt_resposta))
            cd_resposta = cursor.lastrowid
            cursor.execute("update questao_anamnese set cd_resposta = %s where cd_questao = %s and cd_anamnese = %s", (cd_resposta, cd_questao, cd_anamnese))
    bd.commit()
    #cursor.execute(f"SELECT cd_questao_anamnese FROM questao_anamnese WHERE cd_anamnese = {cd_anamnese}")
    #questao = cursor.fetchall()
    #cursor.execute("SELECT cd_paciente FROM anamnese WHERE cd_anamnese = %s",(cd_anamnese,))
    #(cd_paciente,) = cursor.fetchone()
    #adicional = f"CD_QUESTÃO: {cd_questao}, cd_resposta: {cd_resposta} cd_anamnese: {cd_anamnese}"
    #registrar_log('CRQ', cd_paciente=cd_paciente, ADICIONAL=adicional)
    bd.close()
    return jsonify({"MSG242":enviar_mensagem_positiva("MSG242"), "cd_anamnese": cd_anamnese}),201

def remover_anamnese(cd_anamnese):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT cd_paciente FROM anamnese WHERE cd_anamnese = %s", (cd_anamnese,))
        (cd_paciente,) = cursor.fetchone()
        sql = "DELETE FROM anamnese WHERE cd_anamnese = %s"
        cursor.execute(sql, (cd_anamnese,))
        bd.commit()
        #registrar_log('RAN', cd_paciente=cd_paciente)
        return jsonify({"MSG243":enviar_mensagem_positiva("MSG243")}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao deletar anamnese: {e}"})
    finally:
        bd.close()