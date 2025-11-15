from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Controller.log import registrar_log
from Database.database import load_dotenv
import os
load_dotenv()

senha = os.getenv("CRIPT_PASSWORD")

def carregar_medicamento():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_medicamento, CAST(AES_DECRYPT(nm_medicamento, %s) AS CHAR) AS nm_medicamento FROM medicamento", (senha,))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_medicamento_porIdPaciente(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT med.cd_medicamento, CAST(AES_DECRYPT(med.nm_medicamento, %s) AS CHAR) AS nm_medicamento, pmed.dias_ministracao, pmed.dose, CAST(pmed.datas as CHAR) as datas FROM medicamento med LEFT JOIN paciente_medicamento pmed ON pmed.cd_medicamento = med.cd_medicamento WHERE cd_paciente = %s", (senha, cd_paciente))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def criar_medicamento(nm_medicamento, dosagem, forma_farmaceutica, principio_ativo, fabricante, cd_paciente=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    camposG = locals()
    for i in range(2):
        camposG.popitem()
    for campo in camposG:
        valor = camposG[campo]
        if valor == None or campo in ("nm_medicamento", "fabricante"):
            continue
        else:
            valor = " ".join(str(valor).split())
            valor = valor.capitalize()
            camposG[campo] = valor
    try:
#--------------------COMEÇO DAS RNs DO CREATE-------------------------------------------------        
        cursor.execute("SELECT COUNT(*) FROM medicamento WHERE nm_medicamento = AES_ENCRYPT(%s, %s) AND dosagem = %s", (camposG['nm_medicamento'], senha, camposG['dosagem']))
        (existe,) = cursor.fetchone()
        if existe > 0: return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
        
        if not nm_medicamento or not dosagem:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        for campo, valor in list(camposG.items()):
            if valor == "" or valor == None or campo in ("dosagem"):
                continue
            elif ((len(valor) < 3) or (len(valor) > 100)):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
#------------------FIM DAS REGRAS DE NEGÓCIO DO CREATE----------------------------------------      
        sql = "INSERT INTO medicamento (nm_medicamento, dosagem, forma_farmaceutica, principio_ativo, fabricante) VALUES (AES_ENCRYPT(%s, %s), %s, %s, AES_ENCRYPT(%s, %s), %s"
        cursor.execute(sql, (camposG['nm_medicamento'], senha, camposG["dosagem"], camposG["forma_farmaceutica"], camposG["principio_ativo"], senha, camposG["fabricante"]))
        cd_medicamento = cursor.lastrowid
        bd.commit()
        #Registra Log
        adicional = f"'{camposG['nm_medicamento']}', com a dosagem '{camposG['dosagem']}', em forma de '{camposG['forma_farmaceutica']}', principio_ativo de '{camposG['principio_ativo']}', do fabricante '{camposG['fabricante']}'. cd_medicamento: {cd_medicamento}"
        #registrar_log('CMD', ADICIONAL=adicional)
        return jsonify({"MSG235":enviar_mensagem_positiva("MSG235"), "cd_medicamento":cd_medicamento}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar medicamento: {e}"}),400
    finally:
        bd.close()

def atualizar_medicamento(cd_medicamento,nm_medicamento=None, dosagem=None, forma_farmaceutica=None, principio_ativo=None, fabricante=None):
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
#-----------------------------COMEÇO DAS RNs DO UPDATE----------------------------------------

        cursor.execute("SELECT COUNT(*) FROM medicamento WHERE nm_medicamento = AES_ENCRYPT(%s, %s) AND dosagem = %s AND cd_medicamento != %s", (camposG['nm_medicamento'], senha, camposG['dosagem'], cd_medicamento))
        (existe,) = cursor.fetchone()
        if existe > 0: return jsonify({"MSG211": enviar_mensagem_negativa("MSG211")}),400
        
        if not nm_medicamento or not dosagem: return jsonify({"MSG200": enviar_mensagem_negativa("MSG200")}),400
            
        for campo, valor in list(camposG.items())[1:]:
            if valor == "" or valor == None or campo in ("dosagem"):
                continue
            elif((len(valor) < 3) or (len(valor) > 100)):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
#-----------------------------FIM DAS RNs DO UPDATE-------------------------------------------   
        partes_sql = []
        valores = []
        
        if nm_medicamento:
            partes_sql.append("nm_medicamento = AES_ENCRYPT(%s, %s)")
            valores.append(camposG['nm_medicamento'])
            valores.append(senha)
        if dosagem:
            partes_sql.append("dosagem = %s")
            valores.append(camposG['dosagem'])
        if forma_farmaceutica:
            partes_sql.append("forma_farmaceutica = %s")
            valores.append(camposG['forma_farmaceutica'])
        if principio_ativo:
            partes_sql.append("principio_ativo = AES_ENCRYPT(%s, %s)")
            valores.append(camposG['principio_ativo'])
            valores.append(senha)
        if fabricante:
            partes_sql.append("fabricante = %s")
            valores.append(camposG['fabricante'])

        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204")}),204

        sql = f"UPDATE medicamento SET {', '.join(partes_sql)} WHERE cd_medicamento = %s"
        valores.append(cd_medicamento)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        #Registra log
        adicional = adicional = f"'{camposG['nm_medicamento']}', com a dosagem '{camposG['dosagem']}', em forma de '{camposG['forma_farmaceutica']}', principio_ativo de '{camposG['principio_ativo']}', do fabricante '{camposG['fabricante']}'. cd_medicamento: {cd_medicamento}"
        #registrar_log('ADMD', ADICIONAL=adicional)
        return jsonify({"MSG236":enviar_mensagem_positiva("MSG236"), "cd_medicamento": cd_medicamento}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao atualizar medicamento: {e}"}),400
    finally:
        bd.close()

def deletar_medicamento(cd_medicamento):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT CAST(AES_DECRYPT(nm_medicamento, %s) AS CHAR), dosagem, fabricante FROM medicamento WHERE cd_medicamento = %s", (senha, cd_medicamento))
        nm_medicamento, dosagem, fabricante = cursor.fetchone()
        sql = "DELETE FROM medicamento WHERE cd_medicamento = %s"
        cursor.execute(sql, (cd_medicamento,))
        bd.commit()
        #Registra log
        adicional = f"'{nm_medicamento}', dosagem sendo '{dosagem}' e fabricante '{fabricante}'. cd_medicamento: {cd_medicamento}"
        #registrar_log('RMD', ADICIONAL=adicional)
        return jsonify({"MSG237":enviar_mensagem_positiva("MSG237"), 'cd_medicamento': cd_medicamento}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar medicamento: {e}"}),400
    finally:
        bd.close()

"""def inativar_medicamento(cd_medicamento):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT ativo FROM medicamento WHERE cd_medicamento = %s", (cd_medicamento,))
        resultado = cursor.fetchone()

        if not resultado:
            print(f"medicamento com código {cd_medicamento} não encontrado!")
            return

        estado_atual = resultado[0]
        novo_estado = 'N' if estado_atual == 'S' else 'S'

        cursor.execute("UPDATE medicamento SET ativo = %s WHERE cd_medicamento = %s", 
                      (novo_estado, cd_medicamento))
        bd.commit()

        print(f"Medicamentos {cd_medicamento} alterado de '{estado_atual}' para '{novo_estado}' com sucesso!")

    except Exception as e:
        bd.rollback()
        print(f"Erro ao alterar estado d medicamento: {e}")

    finally:
        bd.close()"""