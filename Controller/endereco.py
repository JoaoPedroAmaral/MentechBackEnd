from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Controller.log import registrar_log

def carregar_endereco():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT * FROM endereco")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_endereco_by_id(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT * FROM endereco WHERE cd_paciente = %s", (cd_paciente,))
    linha = cursor.fetchone()
    bd.close()
    return linha if linha else None

def criar_endereco(cd_paciente,tipo, cd_responsavel, cidade, bairro, logradouro, cep, uf, complemento, numero):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    
    try:      
        
        if not cep: 
            return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}), 400
        
        if (cd_responsavel in [None, '', 'null', 'None'] and tipo == "RESPONSAVEL"):
            return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}),400

        if tipo == "PACIENTE":
            cursor.execute("SELECT COUNT(*) FROM endereco WHERE cd_paciente = %s AND cep = %s", (cd_paciente, cep))
        else:
            cursor.execute("SELECT COUNT(*) FROM endereco WHERE cd_paciente = %s AND cep = %s AND cd_responsavel = %s", (cd_paciente, cep, cd_responsavel))
        (existe, ) = cursor.fetchone()
            
        if existe > 0:
            return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400  

        sql = "INSERT INTO endereco (cd_paciente,tipo, cd_responsavel, cidade, bairro, logradouro, cep, uf, complemento, numero) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (cd_paciente,tipo, cd_responsavel, cidade, bairro, logradouro, cep, uf, complemento, numero))
        cd_endereco = cursor.lastrowid
        bd.commit()
        adicional = f"cep: {cep}, do tipo '{tipo}'. cd_endereco:{cd_endereco}"
        #registrar_log('CEN', cd_paciente=cd_paciente, ADICIONAL=adicional)
        return jsonify({"MSG262": enviar_mensagem_positiva("MSG262"), "cd_endereco": cd_endereco}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error": "Erro ao cadastrar endereço: " + str(e)}),400
    finally:
        bd.close()

def atualizar_endereco(cd_endereco,tipo=None,cd_paciente=None, cd_responsavel=None, cidade=None, bairro=None,logradouro=None, cep=None, uf=None, complemento=None, numero=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()  
   
    try:
        
        if not cep: 
            return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}), 400
        
        if cd_responsavel in [None, '', 'null', 'None'] and tipo == "PACIENTE":
            cd_responsavel = None
        else:
            return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}),400
        
        if tipo == "PACIENTE":
            cursor.execute("SELECT COUNT(*) FROM endereco WHERE cd_paciente = %s AND cep = %s AND cd_endereco != %s", (cd_paciente, cep, cd_endereco))
        else:
            cursor.execute("SELECT COUNT(*) FROM endereco WHERE cd_paciente = %s AND cep = %s AND cd_responsavel = %s AND cd_endereco != %s", (cd_paciente, cep, cd_responsavel, cd_endereco))
        (existe, ) = cursor.fetchone()
            
        if existe > 0:
            return jsonify({"MSG217": enviar_mensagem_negativa("MSG217")}),400
        
        partes_sql = []
        valores = []
        if cd_paciente:
            partes_sql.append("cd_paciente = %s")
            valores.append(cd_paciente)
        if tipo:
            partes_sql.append("tipo = %s")
            valores.append(tipo)
        if cd_responsavel:
            partes_sql.append("cd_responsavel = %s")
            valores.append(cd_responsavel)
        if cidade:
            partes_sql.append("cidade = %s")
            valores.append(cidade)
        if bairro:
            partes_sql.append("bairro = %s")
            valores.append(bairro)
        if logradouro:
            partes_sql.append("logradouro = %s")
            valores.append(logradouro)
        if cep:
            partes_sql.append("cep = %s")
            valores.append(cep)
        if uf:
            partes_sql.append("uf = %s")
            valores.append(uf)
        if complemento:
            partes_sql.append("complemento = %s")
            valores.append(complemento)
        if numero:
            partes_sql.append("numero = %s")
            valores.append(numero)    

        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204")}),204

        
        sql = f"UPDATE endereco SET {', '.join(partes_sql)} WHERE cd_paciente = %s"
        valores.append(cd_endereco)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        adicional = f"cep: {cep}, do tipo '{tipo}'. cd_endereco:{cd_endereco}"
        #registrar_log('ADEN', cd_paciente=cd_paciente, ADICIONAL=adicional)
        return jsonify({"MSG263": enviar_mensagem_positiva("MSG263"), "cd_endereco": cd_endereco}),201

    except Exception as e:
        bd.rollback()
        print(f"Erro ao atualizar a endereço: {e}"),400
    finally:
        bd.close()

def deletar_endereco(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT cep, tipo, cd_endereco FROM endereco WHERE cd_paciente = %s",(cd_paciente,))
        enderecos = cursor.fetchall()
        sql = "DELETE FROM endereco WHERE cd_paciente = %s"
        cursor.execute(sql, (cd_paciente,))
        bd.commit()
        for endereco in enderecos:
            adicional = f"cep: {endereco[0]}, do tipo {endereco[1]}. cd_endereco:{endereco[2]}"
            #registrar_log('REN', cd_paciente=cd_paciente, ADICIONAL=adicional)
        return jsonify({"MSG264": enviar_mensagem_positiva("MSG264")}),200
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao deletar endereço: {e}"}),400
    finally:
        bd.close()