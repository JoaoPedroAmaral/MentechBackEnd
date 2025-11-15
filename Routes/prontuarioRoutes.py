from flask import jsonify, request, Blueprint
from Controller.prontuario import carregar_prontuario, criar_prontuario, deletar_prontuario, carregar_prontuar_porPaciente, atualizar_prontuario

prontuario_bp = Blueprint("prontuario_bp", __name__)


@prontuario_bp.route('/prontuario', methods=['GET'])
def get_metas():
    metas = carregar_prontuario()
    return jsonify(metas)

@prontuario_bp.route('/prontuario/por_paciente/<int:cd_paciente>', methods=['GET'])
def get_metas_porPaciente(cd_paciente):
    metas = carregar_prontuar_porPaciente(cd_paciente)
    return jsonify(metas)


@prontuario_bp.route('/prontuario', methods = ['POST'])
def post_metas():
    data = request.json
    print(data)
    try:
        return criar_prontuario(
            cd_paciente = data.get('cd_paciente'),
            dt_prontuario = data.get('dt_prontuario'),
            txt_prontuario = data.get('txt_prontuario')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@prontuario_bp.route('/prontuario/<int:id>', methods=['PUT'])
def put_meta(id):
    data = request.json
    print(data)
    return atualizar_prontuario(id, **data)

@prontuario_bp.route('/prontuario/<int:id>', methods=['DELETE'])
def deletar_meta_fim(id):
    return deletar_prontuario(id)
