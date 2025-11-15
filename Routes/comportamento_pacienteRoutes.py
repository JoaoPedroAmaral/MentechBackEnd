from flask import jsonify, request, Blueprint
from Controller.comportamento_paciente import carregar_comportamento, carregar_comportamento_PorPaciente, criar_comportamento, atualizar_comportamento, deletar_comportamento

comportamento_paciente_bp = Blueprint("comportamento_paciente_bp", __name__)


@comportamento_paciente_bp.route('/comportamento_paciente', methods=['GET'])
def get_comportamento():
    comportamento = carregar_comportamento()
    return jsonify(comportamento)

@comportamento_paciente_bp.route('/comportamento_paciente/por_paciente/<int:cd_paciente>', methods=['GET'])
def get_comportamento_porIdPaciente(cd_paciente):
    comportamento = carregar_comportamento_PorPaciente(cd_paciente)
    return jsonify(comportamento)

@comportamento_paciente_bp.route('/comportamento_paciente', methods = ['POST'])
def post_comportamento():
    data = request.json
    try:
        return criar_comportamento(
            cd_paciente = data.get('cd_paciente'),
            comportamento_paciente = data.get('comportamento_paciente')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@comportamento_paciente_bp.route('/comportamento_paciente/<int:id>', methods=['PUT'])
def put_comportamento(id):
    data = request.json
    return atualizar_comportamento(id, **data)

@comportamento_paciente_bp.route('/comportamento_paciente/<int:id>', methods=['DELETE'])
def deletar_comportamento_fim(id):
   return deletar_comportamento(id)
    

