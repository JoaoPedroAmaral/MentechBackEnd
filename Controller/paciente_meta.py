from flask import jsonify
from Database.database import conectar_base_de_dados
from datetime import datetime, date
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva

def formatar_data(data):
    if isinstance(data, date):
        return data.strftime("%Y-%m-%d")
    if isinstance(data, str):
        formatos_possiveis = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]
        for formato in formatos_possiveis:
            try:
                return datetime.strptime(data, formato).strftime("%Y-%m-%d")
            except ValueError:
                continue
        raise ValueError(f"Formato de data inválido: {data}")

    raise TypeError("O parâmetro 'data' deve ser uma string ou date")


def carregar_paciente_meta():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_paciente_meta, cd_meta, cd_paciente, CAST(dt_cadastro AS CHAR) AS dt_cadastro, CAST(dt_previsao AS CHAR) AS dt_previsao, CAST(dt_conclusao AS CHAR) AS dt_conclusao, ativo, CAST(datas AS CHAR) AS datas FROM paciente_meta")
    linhas = cursor.fetchall()
    return linhas

def carregar_paciente_meta_por_id(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_paciente_meta, cd_meta, cd_paciente, CAST(dt_cadastro AS CHAR) AS dt_cadastro, CAST(dt_previsao AS CHAR) AS dt_previsao, CAST(dt_conclusao AS CHAR) AS dt_conclusao, ativo, CAST(datas AS CHAR) AS datas FROM paciente_meta WHERE cd_paciente = %s", (cd_paciente,))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def criar_paciente_meta(cd_meta, cd_paciente, dt_previsao):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        hoje = formatar_data(datetime.today().strftime('%d-%m-%Y'))
        dt_previsao = formatar_data(dt_previsao)
        
        if dt_previsao < hoje:
            return jsonify({"MSG260": enviar_mensagem_negativa("MSG260")}),400
            
        sql = "INSERT INTO paciente_meta (cd_meta, cd_paciente, dt_previsao, dt_cadastro) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (cd_meta, cd_paciente, dt_previsao, date.today()))
        bd.commit()
        return jsonify({"MSG194":enviar_mensagem_positiva("MSG194"), "cd_meta": cd_meta, "cd_paciente": cd_paciente, "dt_previsao": dt_previsao}),200
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao criar a meta: {e}"}),400
    finally:
        bd.close()

"""def atualizar_paciente_meta(cd_paciente_meta, cd_meta=None, cd_paciente=None, dt_previsao=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        partes_sql = []
        valores = []
        if cd_meta:
            partes_sql.append("cd_meta = %s")
            valores.append(cd_meta)
        if cd_paciente:
            partes_sql.append("cd_paciente = %s")
            valores.append(cd_paciente)
        if dt_previsao:
            dt_cadastro = formatar_data(dt_previsao)
            partes_sql.append("dt_previsao = %s")
            valores.append(dt_previsao)

        if not partes_sql:
            print("Nada para atualizar.")
            return

        sql = f"UPDATE paciente_meta SET {', '.join(partes_sql)} WHERE cd_paciente_meta = %s"
        valores.append(cd_paciente_meta)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        print("Meta atualizada com sucesso!")
    except Exception as e:
        bd.rollback()
        print(f"Erro ao atualizar a meta: {e}")
    finally:
        bd.close()"""

def deletar_paciente_meta(cd_paciente_meta):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM paciente_meta WHERE cd_paciente_meta = %s"
        cursor.execute(sql, (cd_paciente_meta,))
        bd.commit()
        return jsonify({"MSG197":enviar_mensagem_positiva("MSG197")}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar a meta: {e}"}),400
    finally:
        bd.close()

def concluir_meta(cd_paciente_meta):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute(f"SELECT cd_meta FROM paciente_meta WHERE cd_paciente_meta = {cd_paciente_meta}")
        resultado = cursor.fetchone()

        meta = resultado[0]
        
        if not meta:
            return jsonify({"Success":f"Meta com código {meta} não encontrada!"}),204

        cursor.execute("UPDATE paciente_meta SET ativo = 'C', dt_conclusao = %s WHERE cd_paciente_meta = %s", (date.today(), cd_paciente_meta))
        
        cursor.execute(f"UPDATE meta SET ativo = 'C' WHERE cd_meta = {meta}")
        bd.commit()
        
        return jsonify({"Success":f"Meta {cd_paciente_meta} concluida!"}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao alterar estado da atividade: {e}"}),400

    finally:
        bd.close()
    