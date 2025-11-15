from flask import jsonify, request, Blueprint
from Controller.atividade import carregar_atividade, criar_atividade, inativar_atividade, carregar_atividade_por_id_usuario, carregar_atividade_por_id_paciente, atualizar_atividade, carregar_atividade_por_id_meta, deletar_atividade


atividade_bp = Blueprint("atividade_bp", __name__)


@atividade_bp.route('/atividade', methods=['GET'])
def get_atividade():
    atividades = carregar_atividade()
    return jsonify(atividades)

@atividade_bp.route('/atividade/por_usuario/<int:cd_usuario>', methods=['GET'])
def get_atividade_por_usuario(cd_usuario):
    atividades = carregar_atividade_por_id_usuario(cd_usuario)
    return jsonify(atividades)

@atividade_bp.route('/atividade/por_meta/<int:cd_meta>', methods=['GET'])
def get_atividade_por_meta(cd_meta):
    atividades = carregar_atividade_por_id_meta(cd_meta)
    return jsonify(atividades)

@atividade_bp.route('/atividade/por_paciente/<int:cd_paciente>', methods=['GET'])
def get_atividade_por_paciente(cd_paciente):
    atividades = carregar_atividade_por_id_paciente(cd_paciente)
    return jsonify(atividades)

#nm_atividade, descricao_atividade, dt_atividade, parecer_tecnico, resultado, cd_meta
@atividade_bp.route('/atividade', methods = ['POST'])
def post_atividade():
    data = request.json
    try:
        return criar_atividade(
            nm_atividade = data.get('nm_atividade'),
            descricao_atividade = data.get('descricao_atividade'),
            dt_atividade = data.get('dt_atividade'),
            parecer_tecnico = data.get('parecer_tecnico'),
            resultado = data.get('resultado'),
            cd_meta = data.get('cd_meta')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@atividade_bp.route('/atividade/<int:id>', methods=['PUT'])
def put_atv(id):
    data = request.json
    return atualizar_atividade(id, **data)
    
@atividade_bp.route('/atividade/inativar/<int:id>', methods=['PUT'])
def put_inativar_atividade(id):
    return inativar_atividade(id)

@atividade_bp.route('/atividade/<int:id>', methods=['DELETE'])
def deletar_atividade_fim(id):
    deletar_atividade(id)
    return jsonify({"message": "Atividade deletada com sucesso!"})
