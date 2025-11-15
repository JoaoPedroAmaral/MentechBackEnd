from flask import jsonify, request, Blueprint
from Controller.paciente_medicamento import carregar_paciente_medicamento, criar_paciente_medicamento, deletar_paciente_medicamento, atualizar_paciente_medicamento, carregar_medicamento_por_paciente

paciente_medicamento_bp = Blueprint("paciente_medicamento_bp", __name__)

@paciente_medicamento_bp.route('/paciente_medicamento', methods=['GET'])
def get_paciente_medicamento():
    paciente_medicamento = carregar_paciente_medicamento()
    return jsonify(paciente_medicamento)

@paciente_medicamento_bp.route('/paciente_medicamento/<int:cd_paciente>', methods=['GET'])
def get_medicamento_por_paciente(cd_paciente):
    medicamentos = carregar_medicamento_por_paciente(cd_paciente)
    if not medicamentos:
        return jsonify({"error": "Nenhum medicamento encontrado para este paciente."}), 404
    return jsonify(medicamentos)

@paciente_medicamento_bp.route('/paciente_medicamento', methods=['POST'])
def post_paciente_medicamento():
    data = request.json
    try:
        return criar_paciente_medicamento(
            cd_paciente = data.get('cd_paciente'),
            cd_medicamento = data.get('cd_medicamento'),
            dias_ministracao = data.get('dias_ministracao'),
            dose = data.get('dose')
        )
    except Exception as e:
        return jsonify({"error":str(e)}), 400
    
#adicionar PUT se preciso
@paciente_medicamento_bp.route('/paciente_medicamento/<int:id>', methods=['PUT'])
def put_paciente_medicamento(id):
    data = request.json
    return atualizar_paciente_medicamento(id, **data)
    
@paciente_medicamento_bp.route('/paciente_medicamento/<int:id>', methods=['DELETE'])
def deletar_paciente_medicamento_fim(id):
    return deletar_paciente_medicamento(id)
    