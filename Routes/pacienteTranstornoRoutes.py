from flask import jsonify, request, Blueprint
from Controller.paciente_transtorno import carregar_paciente_transtorno, criar_paciente_transtorno, deletar_paciente_transtorno, deletarTodos_paciente_transtorno

pacienteTranstorno_bp = Blueprint("pacienteTranstorno_bp", __name__)

@pacienteTranstorno_bp.route('/pacienteTranstorno', methods=['GET'])
def get_pacienteTranstorno():
    pacienteTranstorno = carregar_paciente_transtorno()
    return jsonify(pacienteTranstorno)

@pacienteTranstorno_bp.route('/pacienteTranstorno', methods=['POST'])
def post_pacienteTranstorno():
    data = request.json
    try:
        return criar_paciente_transtorno(
            cd_paciente=data.get('cd_paciente'),
            cd_transtorno=data.get('cd_transtorno'),
            datas=data.get('datas')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@pacienteTranstorno_bp.route('/pacienteTranstorno/<int:id>', methods=['DELETE'])
def delete_pacienteTranstorno_fim(id):
    return deletar_paciente_transtorno(id)

@pacienteTranstorno_bp.route('/pacienteTranstorno/all/<int:id>', methods=['DELETE'])
def deleteTodos_pacienteTranstorno_fim(id):
    return deletarTodos_paciente_transtorno(id)