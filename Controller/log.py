from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_positiva
import os
from datetime import datetime
def definir_usuario(USUARIO_LOGADO):
    global USUARIO
    USUARIO = USUARIO_LOGADO
    return USUARIO

def registrar_log(tipo_log, cd_paciente=None, CD_TRANSOTRNO=None, meta=None, ADICIONAL=None):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    (mensagem, ) = enviar_mensagem_positiva(tipo_log)
    if ADICIONAL != None:
        mensagem += ADICIONAL
    dia = datetime.today().strftime('%Y-%m-%d')
    sql = 'INSERT INTO log_acao (cd_usuario, tipo_log, mensagem, dt_log, cd_paciente, cd_transtorno, cd_meta) VALUES (%s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(sql, (USUARIO, tipo_log, mensagem, dia, cd_paciente, CD_TRANSOTRNO, meta))
    bd.commit()
    
def registrar_log_alterar_senha(tipo_log, cd_paciente=None, CD_TRANSOTRNO=None, cd_meta=None, ADICIONAL=None, cd_usuario=None):    
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    (mensagem, ) = enviar_mensagem_positiva(tipo_log)
    mensagem += ADICIONAL+'.'
    dia = datetime.today().strftime('%Y-%m-%d')
    sql = 'INSERT INTO log_acao (cd_usuario, tipo_log, mensagem, dt_log, cd_paciente, cd_transtorno, cd_meta) VALUES (%s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(sql, (cd_usuario, tipo_log, mensagem, dia, cd_paciente, CD_TRANSOTRNO, cd_meta))
    bd.commit()
    
    
    