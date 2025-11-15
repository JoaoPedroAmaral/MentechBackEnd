from datetime import datetime, date
from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_positiva, enviar_mensagem_negativa
from Controller.log import registrar_log
from Database.database import load_dotenv
import os
load_dotenv()
senha = os.getenv("CRIPT_PASSWORD")
tamanhos = {'nm_paciente': 100, 'cid11': 7, 'dt_nasc': 10, 'sexo': 50, 'tip_sang': 50, 'ANAMNESE': 2000}

def formatar_data(data):
    try:
        if "-" in data:
            if len(data.split("-")[0]) == 4: 
                return data
            else:
                formato = "%d-%m-%Y"
        elif "/" in data:
            formato = "%d/%m/%Y"
        else:
            raise ValueError(f"Formato de data inválido: {data}")

        return datetime.strptime(data, formato).strftime("%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"Erro ao converter data '{data}': {e}")

def adicional_log(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""SELECT
                              p.nm_paciente,
                              cast(p.dt_nasc as CHAR) as dt_nascimento, 
                              CAST(AES_DECRYPT(p.sexo, %s) AS CHAR) AS sexo, 
                              CAST(AES_DECRYPT(g.nm_genero, %s) AS CHAR) AS nm_genero,
                              CAST(AES_DECRYPT(p.tip_sang, %s) AS CHAR) AS tip_sang,
                              prfl.perfil
                        FROM paciente p
                        LEFT JOIN genero g 
                            ON g.cd_genero = p.cd_genero
                        LEFT JOIN perfil prfl
                            ON p.cd_perfil = prfl.cd_perfil
                        WHERE cd_paciente = %s""", (senha, senha, senha, cd_paciente))
    linha = cursor.fetchone()
    bd.close()
    return linha

def carregar_paciente():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""SELECT p.cd_paciente,
                              p.nm_paciente,
                              cast(p.dt_nasc as CHAR) as dt_nascimento, 
                              CAST(AES_DECRYPT(p.sexo, %s) AS CHAR) AS sexo, 
                              CAST(AES_DECRYPT(g.nm_genero, %s) AS CHAR) AS nm_genero,
                              CAST(AES_DECRYPT(p.tip_sang, %s) AS CHAR) AS tip_sang,
                              prfl.perfil,
                              p.ativo 
                        FROM paciente p
                        LEFT JOIN genero g 
                            ON g.cd_genero = p.cd_genero
                        LEFT JOIN perfil prfl
                            ON p.cd_perfil = prfl.cd_perfil""", (senha, senha, senha))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_paciente_por_id(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""SELECT p.cd_paciente,
                              p.nm_paciente,
                              cast(p.dt_nasc as CHAR) as dt_nascimento, 
                              CAST(AES_DECRYPT(p.sexo, %s) AS CHAR) AS sexo, 
                              CAST(AES_DECRYPT(g.nm_genero, %s) AS CHAR) AS nm_genero,
                              CAST(AES_DECRYPT(p.tip_sang, %s) AS CHAR) AS tip_sang,
                              prfl.cd_perfil,
                              p.ativo 
                        FROM paciente p
                        LEFT JOIN genero g 
                            ON g.cd_genero = p.cd_genero
                        LEFT JOIN perfil prfl
                            ON p.cd_perfil = prfl.cd_perfil
                        WHERE cd_paciente = %s""", (senha, senha, senha, cd_paciente))
    linha = cursor.fetchone()
    bd.close()
    return linha

def carregar_pacientes_por_id_usuario(cd_usuario):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("""SELECT p.cd_paciente, 
                              up.cd_usuario,
                              p.nm_paciente,
                              cast(p.dt_nasc as CHAR) as dt_nascimento, 
                              CAST(AES_DECRYPT(p.sexo, %s) AS CHAR) AS sexo, 
                              CAST(AES_DECRYPT(g.nm_genero, %s) AS CHAR) AS nm_genero,  
                              CAST(AES_DECRYPT(p.tip_sang, %s) AS CHAR) AS tip_sang,
                              -- prfl.perfil,
                              p.ativo 
                        FROM paciente p 
                        JOIN usuario_paciente up 
                            ON p.cd_paciente = up.cd_paciente
                        LEFT JOIN genero g 
                            ON g.cd_genero = p.cd_genero
                        LEFT JOIN perfil prfl
                            ON prfl.cd_perfil = p.cd_perfil 
                        WHERE up.cd_usuario = %s""", (senha, senha, senha, cd_usuario))
    linha = cursor.fetchall()
    bd.close()
    return linha

def carregar_anamnese_por_id(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"""SELECT cd_paciente,
                              nm_paciente,
                        FROM paciente p
                        WHERE cd_paciente = {cd_paciente}""")
    linha = cursor.fetchone()
    bd.close()
    return linha


def criar_paciente(nm_paciente, dt_nasc, sexo, cd_genero, tip_sang, cd_perfil, cd_usuario):
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
        dt_nasc = formatar_data(dt_nasc)
        
        if not nm_paciente or not sexo:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        for campo, valor in list(camposG.items()):
            if valor == "" or valor == None or campo not in tamanhos.keys():
                continue
            elif ((len(valor) < 3 and campo not in ['sexo', 'tip_sang']) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
#------------------FIM DAS REGRAS DE NEGÓCIO DO CREATE----------------------------------------  
        sql = "INSERT INTO paciente(nm_paciente, dt_nasc, sexo, cd_genero, tip_sang, cd_perfil) VALUES (%s,%s,AES_ENCRYPT(%s, %s),%s,AES_ENCRYPT(%s, %s), %s)"
        cursor.execute(sql, (camposG['nm_paciente'], camposG['dt_nasc'], camposG['sexo'], senha, camposG['cd_genero'], camposG['tip_sang'], senha, camposG['cd_perfil']))
        bd.commit()
        cd_paciente = cursor.lastrowid
        cursor.execute(f"INSERT INTO usuario_paciente (cd_usuario, cd_paciente) VALUES ({cd_usuario}, {cd_paciente})")
        adicional = ", ".join(str(valor) for valor in adicional_log(cd_paciente).values())
        #registrar_log('CNP', cd_paciente=cd_paciente, ADICIONAL=adicional)
        bd.commit()  
        return jsonify({"MSG057":enviar_mensagem_positiva("MSG057"),"cd_paciente":cd_paciente, "inseridos": f"{camposG['nm_paciente']}, {camposG['dt_nasc']}, {camposG['sexo']}, {camposG['cd_genero']}, {camposG['tip_sang']}, {camposG['cd_perfil']}"}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar paciente! {e}"}),400
    finally:
        bd.close()

def cadastrar_anamnese(cd_paciente, ANAMNESE):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        if not ANAMNESE:
            return jsonify({"MSG200":enviar_mensagem_negativa("MSG200")}),400
        sql = "UPDATE paciente SET ANAMNESE = %s WHERE cd_paciente = %s"
        cursor.execute(sql, (ANAMNESE, cd_paciente))
        bd.commit()
        return jsonify({"MSG241": enviar_mensagem_positiva("MSG241"), "cd_paciente": cd_paciente}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao cadastrar anamnese: {e}"}),400
    finally:
        bd.close()

def atualizar_paciente(cd_paciente, nm_paciente = None, dt_nascimento = None, sexo = None, cd_genero = None, tip_sang = None, cd_perfil = None):
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
        partes_sql = []
        valores = []
        
        if nm_paciente:
            partes_sql.append("nm_paciente = %s")
            valores.append(camposG['nm_paciente'])
        if dt_nascimento:
            dt_nascimento = formatar_data(dt_nascimento)
            partes_sql.append("dt_nasc = %s")
            valores.append(camposG['dt_nascimento'])
        if sexo:
            partes_sql.append("sexo = AES_ENCRYPT(%s, %s)")
            valores.append(camposG['sexo'])
            valores.append(senha)
        if cd_genero:
            partes_sql.append("cd_genero = %s")
            valores.append(camposG['cd_genero'])
        if tip_sang:
            partes_sql.append("tip_sang = AES_ENCRYPT(%s, %s)")
            valores.append(camposG['tip_sang'])
            valores.append(senha)
        if cd_perfil:
            partes_sql.append("cd_perfil = %s")
            valores.append(camposG['cd_perfil'])
        if not partes_sql:
            return jsonify({"MSG204":enviar_mensagem_negativa("MSG204"), "cd_paciente":cd_paciente}),400

#-----------------------------COMEÇO DAS RNs DO UPDATE----------------------------------------     
        for campo, valor in list(camposG.items())[1:]:
            if valor == "" or valor == None or campo not in tamanhos.keys():
                continue
            elif ((len(valor) < 3 and campo not in ['sexo', 'tip_sang']) or (len(valor) > tamanhos[campo])):
                return jsonify({"MSG199":enviar_mensagem_negativa("MSG199")}),400
            
        sql = f"UPDATE paciente SET {', '.join(partes_sql)} WHERE cd_paciente = %s"
        valores.append(cd_paciente)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return jsonify({"MSG058": enviar_mensagem_positiva("MSG058"), "cd_paciente":cd_paciente}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao atualizar paciente {e}"}),400
    finally:
        bd.close()
        
# def deletar_paciente(cd_paciente):
#     bd = conectar_base_de_dados()
#     cursor = bd.cursor()
#     try:
#         sql = "DELETE FROM paciente WHERE cd_paciente = %s"
#         cursor.execute(sql, (cd_paciente,))
#         bd.commit()
#         print("Paciente deletado com sucesso!")
#     except Exception as e:
#         bd.rollback()
#         print(f"Erro ao deletar Paciente: {e}")
#     finally:
#         bd.close()

def inativar_paciente(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT ativo FROM paciente WHERE cd_paciente = %s", (cd_paciente,))
        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({"MSG217":enviar_mensagem_positiva("MSG217"), "cd_paciente":cd_paciente}),204

        estado_atual = resultado[0]
        novo_estado = ""
        if estado_atual == 'N': novo_estado = 'S'
        else: novo_estado = 'N'

        cursor.execute("UPDATE paciente SET ativo = %s WHERE cd_paciente = %s", 
                      (novo_estado, cd_paciente))
        bd.commit()

        return jsonify({"MSG218":enviar_mensagem_positiva("MSG218"), "Paciente":cd_paciente}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao alterar estado do paciente: {e}"}),400

    finally:
        bd.close()