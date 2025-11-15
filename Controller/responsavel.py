from flask import jsonify
from Database.database import conectar_base_de_dados
from datetime import datetime

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


def carregar_responsavel():
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    cursor.execute("SELECT * FROM responsavel")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_responsavel_by_id(cd_paciente):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)  # Usar cursor com dicionário para facilitar o acesso aos campos
    try:
        sql = "SELECT * FROM responsavel WHERE cd_paciente = %s"
        cursor.execute(sql, (cd_paciente,))
        resultado = cursor.fetchall()
        if resultado:
            # Converter a data manualmente para string YYYY-MM-DD
            for r in resultado:
                if "dt_nascimento" in r and r["dt_nascimento"]:
                    r["dt_nascimento"] = r["dt_nascimento"].strftime("%Y-%m-%d")
            return jsonify(resultado)
        else:
            return jsonify({"error": "Responsável não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": f"Erro ao carregar responsável: {e}"}), 400
    finally:
        bd.close()

def criar_responsavel(cd_paciente, cpf, nome, dt_nascimento):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        dt_nascimento = formatar_data(dt_nascimento)
            
        sql = "INSERT INTO responsavel (cd_paciente, cpf, nome, dt_nascimento) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (cd_paciente, cpf, nome, dt_nascimento))
        bd.commit()
        cd_responsavel = cursor.lastrowid  
        return jsonify({"Success": "Responsavel criado com sucesso!", "cd_responsavel": cd_responsavel}),201
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao criar responsavel: {e}"}),400
    finally:
        bd.close()

def atualizar_responsavel(cd_responsavel, cd_paciente=None ,cpf=None, nome=None, dt_nascimento=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        partes_sql = []
        valores = []
        if cd_paciente:
            partes_sql.append("cd_paciente = %s")
            valores.append(cd_paciente)
        if cpf:
            partes_sql.append("cpf = %s")
            valores.append(cpf)
        if nome:
            partes_sql.append("nome = %s")
            valores.append(nome)
        if dt_nascimento:
            dt_nascimento = formatar_data(dt_nascimento)
            partes_sql.append("dt_nascimento = %s")
            valores.append(dt_nascimento)

        if not partes_sql:
            return jsonify({"Success": "Nada para atualizar."}),204


        sql = f"UPDATE responsavel SET {', '.join(partes_sql)} WHERE cd_responsavel = %s"
        valores.append(cd_responsavel)
        cursor.execute(sql, tuple(valores))
        bd.commit()
        return jsonify({"Success": "Responsavel atualizado com sucesso!"}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao atualizar responsavel: {e}"}),400
    finally:
        bd.close()



def deletar_responsavel_porID(cd_responsavel):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM responsavel WHERE cd_paciente = %s"
        cursor.execute(sql, (cd_responsavel,))
        bd.commit()
        return jsonify({"Success": "Responsavel deletado com sucesso!"}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar responsavel: {e}"}),400
    finally:
        bd.close()
        
def deletar_responsavel(cd_responsavel):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        sql = "DELETE FROM responsavel WHERE cd_responsavel = %s"
        cursor.execute(sql, (cd_responsavel,))
        bd.commit()
        return jsonify({"Success": "Responsavel deletado com sucesso!"}),201

    except Exception as e:
        bd.rollback()
        return jsonify({"error":f"Erro ao deletar responsavel: {e}"}),400
    finally:
        bd.close()