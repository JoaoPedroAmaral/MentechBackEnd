from flask import jsonify, request, Blueprint
from Controller.medicamento import deletar_medicamento, carregar_medicamento, criar_medicamento, atualizar_medicamento, carregar_medicamento_porIdPaciente
medicamento_bp = Blueprint("medicamento_bp", __name__)


@medicamento_bp.route('/medicamento', methods=['GET'])
def get_medicamento():
    medicamento = carregar_medicamento()
    return jsonify(medicamento)

@medicamento_bp.route('/medicamento/por_paciente/<int:cd_paciente>', methods=['GET'])
def get_medicamento_porIdPaciente(cd_paciente):
    medicamento = carregar_medicamento_porIdPaciente(cd_paciente)
    return jsonify(medicamento)

@medicamento_bp.route('/medicamento', methods = ['POST'])
def post_medicamento():
    data = request.json
    try:
        return criar_medicamento(
            nm_medicamento = data.get('nm_medicamento'),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@medicamento_bp.route('/medicamento/<int:id>', methods=['PUT'])
def put_medicamento(id):
    data = request.json
    return atualizar_medicamento(id, **data)

@medicamento_bp.route('/medicamento/<int:id>', methods=['DELETE'])
def deletar_medicamento_fim(id):
    return deletar_medicamento(id)
    

"""@medicamento_bp.route('/medicamento/<int:id>', methods=['PUT'])
def inativar_medicamento(id):
    inativar_medicamento(id)
    return jsonify({"message": "medicamento inativado com sucesso!"})"""

