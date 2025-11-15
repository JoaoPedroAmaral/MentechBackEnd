from flask import jsonify
from Database.database import conectar_base_de_dados
from datetime import datetime, date
from Database.database import load_dotenv
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
import os

load_dotenv()

senha = os.getenv("CRIPT_PASSWORD")

tamanhos = {'txt_prontuario':500}
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


def carregar_prontuario():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_prontuario, cd_paciente, CAST(AES_DECRYPT(txt_prontuario, %s) AS CHAR) AS txt_prontuario, CAST(dt_prontuario AS CHAR) AS dt_prontuario FROM prontuario;", (senha))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_prontuar_porPaciente(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_prontuario, cd_paciente, CAST(AES_DECRYPT(txt_prontuario, %s) AS CHAR) AS txt_prontuario, CAST(dt_prontuario AS CHAR) AS dt_prontuario FROM prontuario WHERE cd_paciente = %s;", (senha, cd_paciente))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def criar_prontuario(cd_paciente, dt_prontuario, txt_prontuario):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    dt_prontuario = formatar_data(dt_prontuario)
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
        if not cd_paciente:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        for campo, valor in list(camposG.items()):
            if valor == "" or valor == None or campo not in tamanhos.keys():
                continue
            if campo == "txt_prontuario":
                continue
            elif ((len(valor) < 4) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400 

        # cursor.execute("SELECT COUNT(*) FROM prontuario WHERE cd_paciente = %s AND dt_prontuario = %s", (cd_paciente, camposG["dt_prontuario"]))
        # (existe,) = cursor.fetchone()
        # if existe > 0: return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400    
#------------------FIM DAS REGRAS DE NEGÓCIO DO CREATE----------------------------------------
        sql ="""
        INSERT INTO prontuario (cd_paciente, dt_prontuario, txt_prontuario)
        VALUES (%s, %s, AES_ENCRYPT(%s, %s))
        """
        cursor.execute(sql, (cd_paciente, dt_prontuario, txt_prontuario, senha))
        cd_prontuario = cursor.lastrowid  
        bd.commit()
        return jsonify({"MSG238":enviar_mensagem_positiva("MSG238"), 'cd_prontuario':cd_prontuario}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar prontuario: {e}"}),400
    finally:
        bd.close()


def atualizar_prontuario(cd_prontuario, cd_paciente = None, dt_prontuario = None, txt_prontuario = None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    dt_prontuario = formatar_data(dt_prontuario)
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        if valor == None:
            continue
        # else:
        #     valor = " ".join(str(valor).split())
        #     valor = valor.capitalize()
        #     camposG[campo] = valor
        if campo != "txt_prontuario":
            valor = " ".join(str(valor).split())
            valor = valor.capitalize()
        camposG[campo] = valor
    try:
        partes_sql = []
        valores = []
        if cd_paciente:
            partes_sql.append("cd_paciente = %s")
            valores.append(camposG['cd_paciente'])
        if dt_prontuario:
            partes_sql.append("dt_prontuario = %s")
            valores.append(camposG['dt_prontuario'])
        if txt_prontuario:
            partes_sql.append("txt_prontuario = AES_ENCRYPT(%s, %s)")
            valores.append(camposG['txt_prontuario'])
            valores.append(senha)
        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204")}),204
        
#-----------------------------COMEÇO DAS RNs DO UPDATE----------------------------------------
        if not cd_paciente:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        
        cursor.execute("SELECT COUNT(*) FROM prontuario WHERE cd_paciente = %s AND dt_prontuario = %s AND txt_prontuario = AES_ENCRYPT(%s, %s)", (cd_paciente, camposG["dt_prontuario"], camposG['txt_prontuario'], senha))
        (existe,) = cursor.fetchone()
        if existe > 0: return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400    
#-----------------------------FIM DAS RNs DO UPDATE-------------------------------------------
        sql = f"UPDATE prontuario SET {', '.join(partes_sql)} WHERE cd_prontuario = %s"
        valores.append(cd_prontuario)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return jsonify({"MSG239":enviar_mensagem_positiva("MSG239"), "cd_prontuario": cd_prontuario}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao atualizar transtorno: {e}"})
    finally:
        bd.close()

def deletar_prontuario(cd_prontuario):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM prontuario WHERE cd_prontuario = %s"
        cursor.execute(sql, (cd_prontuario,))
        bd.commit()
        return jsonify({"MSG240":enviar_mensagem_positiva("MSG240")}),201
    except Exception as e:
        bd.rollback()
        print(f"Erro ao deletar prontuario: {e}")
        return jsonify({"error":f"Erro ao deletar prontuario: {e}"}),400
    finally:
        bd.close()