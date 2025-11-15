from flask import jsonify
from Database.database import conectar_base_de_dados

def carregar_percent_atividades():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT * FROM hst_percent_atividade")
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def historico_da_atividade(cd_atividade):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"SELECT h.percent_conclusao, h.dt_atualizacao, a.nm_atividade FROM hst_percent_atividade h JOIN atividade a ON h.cd_atividade = a.cd_atividade WHERE h.cd_atividade = {cd_atividade};")
    historico = cursor.fetchall()
    bd.close()
    return historico

def historico_atividades_meta(cd_meta):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute(f"SELECT cd_atividade from atividade WHERE cd_meta = {cd_meta}")
    atividades = cursor.fetchall()
    if len(atividades) == 1:
        bd.close()
        return historico_da_atividade(atividades[0])
    elif len(atividades) > 1:
        cursor = bd.cursor(dictionary=True)
        cursor.execute(f"SELECT * from hst_percent_atividade WHERE cd_atividade IN ({', '.join(atividades)})")
        hstrcs = cursor.fetchall()
        bd.close()
        return hstrcs
    else:
        bd.close()
        return jsonify({"Success": "Nenhuma atividade selecionada"}),204
    
    
    
    
    
# def delete_gravidade(cd_gravidade):
#     bd = conectar_base_de_dados()
#     cursor = bd.cursor()
#     try:
#         sql = "DELETE FROM gravidade WHERE cd_gravidade = %s"
#         cursor.execute(sql, (cd_gravidade,))
#         bd.commit()
#         print("Gravidade deletada com sucesso!")
#     except Exception as e:
#         bd.rollback()
#         print(f"Erro ao deletar gravidade: {e}")
#     finally:
#         bd.close()