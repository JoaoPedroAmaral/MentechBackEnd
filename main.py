from Controller.meta import carregar_meta
from Controller.paciente_medicamento import carregar_paciente_medicamento
from Controller.paciente_meta import carregar_paciente_meta
from Controller.paciente import carregar_paciente, carregar_paciente_por_id, carregar_pacientes_por_id_usuario
from Controller.patologia import carregar_patologia, carregar_patologia_by_id
from Controller.prontuario import carregar_prontuario
from Controller.responsavel import carregar_responsavel
from Controller.subtipo_transtorno import carregar_subtipo_transtorno
from Controller.telefone import carregar_telefone
from Controller.transtorno import carregar_transtorno
from Controller.usuario import carregar_usuario
from Controller.meta import carregar_meta
from Controller.atividade import carregar_atividade, carregar_atividade_por_id_usuario
from Controller.criterio_diagnostico import carregar_criterio_diagnostico
from Controller.endereco import carregar_endereco
from Controller.gravidade import carregar_gravidade
from Controller.mensagens import carregar_mensagens
from Controller.medicamento import carregar_medicamento
from Controller.genero import carregar_genero
from Controller.alterar_senha import carregar_pedidos
from Controller.percent_atividades import carregar_percent_atividades

def main():
    medicamento = carregar_medicamento()
    mensagem = carregar_mensagens()
    meta = carregar_meta()
    paciente_medicamento = carregar_paciente_medicamento()
    paciente_meta = carregar_paciente_meta()
    paciente = carregar_paciente()
    paciente_id_paciente = carregar_paciente_por_id(1)
    paciente_id_usuario = carregar_pacientes_por_id_usuario(1)
    patologia = carregar_patologia()
    patologia_por_id = carregar_patologia_by_id(2)
    prontuario = carregar_prontuario()
    responsavel = carregar_responsavel()
    subtipo_transtorno = carregar_subtipo_transtorno()
    telefone = carregar_telefone()
    transtorno = carregar_transtorno()
    usuario = carregar_usuario()
    atividade = carregar_atividade()
    criterio_diagnostico = carregar_criterio_diagnostico()
    endereco = carregar_endereco()
    gravidade = carregar_gravidade()
    genero = carregar_genero()
    alterar_senha = carregar_pedidos()
    atividade_por_id_usuario = carregar_atividade_por_id_usuario(1)
    percent_ativdades = carregar_percent_atividades()


    # print("mensagem:", mensagem)
    # print("atividade:", atividade)
    # print("atividade_por_id_usuario:", atividade_por_id_usuario)
    # print("criterio_diagnostico:", criterio_diagnostico)
    # print("endereco:", endereco)
    # print("gravidade:", gravidade)
    # print("Meta:", meta)
    # print("paciente_medicamento:", paciente_medicamento)
    # print("paciente_meta:", paciente_meta)
    print("paciente:", paciente)
    # print("patologia:", patologia)
    #print("patologiaID:", patologia_por_id)
    # print("prontuario:", prontuario)
    # print("responsavel:", responsavel)
    # print("subtipo_transtorno:", subtipo_transtorno)
    # print("telefone:", telefone)
    # print("transtorno:", transtorno)
    # print("usuario:", usuario)
    # print("medicamento:", medicamento)
    # print("genero:", genero)
    # print("alterar_senha:", alterar_senha)
    #print("Pacientes por id paciente: ", paciente_id_paciente)
    #print("Pacientes pro id do usuario: ", paciente_id_usuario)
    #print("Percent_atividades: ", percent_atividades)
    
if __name__ == "__main__":
    main()
