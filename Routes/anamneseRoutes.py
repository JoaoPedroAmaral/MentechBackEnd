from flask import jsonify, request, Blueprint
from Controller.anamnese import carregar_anamnese, carregar_anamnese_por_cd_paciente, gerar_anamnese_por_perfil_do_paciente, perfis, Alternativas_por_cd_questao, responder_questoes, remover_anamnese

anamnese_bp = Blueprint("anamnese_bp", __name__)

@anamnese_bp.route('/anamnese/perfis', methods=['GET'])
def get_perfis():
    return jsonify(perfis())

@anamnese_bp.route('/anamnese/alternativas/<int:cd_questao>', methods=['GET'])
def get_alternativas(cd_questao):
    alternativas = Alternativas_por_cd_questao(cd_questao)    
    return jsonify(alternativas)

@anamnese_bp.route('/anamnese', methods=['GET'])
def get_anamnese():
    anamneses = carregar_anamnese()
    return jsonify(anamneses)

@anamnese_bp.route('/anamnese/por_paciente/<int:cd_paciente>', methods=['GET'])
def get_anamnese_por_paciente(cd_paciente):
    anamneses = carregar_anamnese_por_cd_paciente(cd_paciente)
    return jsonify(anamneses)

@anamnese_bp.route('/anamnese/gerar_por_perfil', methods=['POST'])
def get_gerar_anamnese_por_perfil():
    data = request.json
    try:
        anamnese = gerar_anamnese_por_perfil_do_paciente(
            cd_perfil = data.get('cd_perfil'),
            cd_paciente = data.get('cd_paciente'))
        return anamnese
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@anamnese_bp.route('/anamnese/resposta', methods = ['POST'])
def post_anamnese():
    data = request.json
    try:
        return responder_questoes(
            cd_questao = data.get('cd_questao'),
            cd_alternativa = data.get('cd_alternativa'),
            txt_resposta = data.get('txt_resposta'),
            cd_anamnese = data.get('cd_anamnese')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@anamnese_bp.route('/anamnese/<int:cd_anamnese>', methods=['DELETE'])
def deletar_atividade_fim(cd_anamnese):
    return remover_anamnese(cd_anamnese)
