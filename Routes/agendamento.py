from flask import jsonify, request, Blueprint
from Controller.agendamento import carregar_agendamentos, carregar_agendamentos_por_id_paciente, carregar_agendamentos_por_id_usuario, criar_agendamento, deletar_agendamento, atualizar_agendamento, comparecimento_paciente

agendamento_bp = Blueprint("agendamento_bp", __name__)


@agendamento_bp.route('/agendamento', methods=['GET'])
def get_agendamento():
    agendamentos = carregar_agendamentos()
    return jsonify(agendamentos)

@agendamento_bp.route('/agendamento/por_usuario/<int:cd_usuario>', methods=['GET'])
def get_agendamento_por_usuario(cd_usuario):
    agendamentos = carregar_agendamentos_por_id_usuario(cd_usuario)
    return jsonify(agendamentos)

@agendamento_bp.route('/agendamento/por_paciente/<int:cd_paciente>', methods=['GET'])
def get_agendamento_por_paciente(cd_paciente):
    agendamentos = carregar_agendamentos_por_id_paciente(cd_paciente)
    return jsonify(agendamentos)

@agendamento_bp.route('/agendamento', methods = ['POST'])
def post_agendamento():
    data = request.json
    try:
        return criar_agendamento(
            cd_paciente = data.get('cd_paciente'),
            cd_usuario = data.get('cd_usuario'),
            dt_agendamento = data.get('dt_agendamento'),
            hora_inicio = data.get('hora_inicio'),
            hora_fim = data.get('hora_fim'),
            prazo= data.get('prazo')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@agendamento_bp.route('/agendamento/<int:id>', methods=['PUT'])
def put_atv(id):
    data = request.json
    return atualizar_agendamento(id, **data)

@agendamento_bp.route('/agendamento/comparecimento/<int:id>', methods=['PUT'])
def put_comparecimento_paciente(id):
    return comparecimento_paciente(id)

@agendamento_bp.route('/agendamento/<int:id>', methods=['DELETE'])
def deletar_agendamento_fim(id):
    return deletar_agendamento(id)