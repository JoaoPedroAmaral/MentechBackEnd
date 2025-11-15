from flask import jsonify, request, Blueprint
from Controller.criterio_diagnostico import carregar_criterio_diagnostico, criar_criterio_diagnostico, deletar_criterio_diagnostico, deletarTodos_criterio_diagnostico,atualizar_criterio_diagnostico, carregar_criterio_diagnostico_porIDTranstorno, deletar_criterioPorIdTranstorno

criterio_diagnostico_bp = Blueprint("criterio_diagnostico_bp", __name__)


@criterio_diagnostico_bp.route('/criterio_diagnostico', methods=['GET'])
def get_criterio_diagnostico():
    criterios = carregar_criterio_diagnostico()
    return jsonify(criterios)

@criterio_diagnostico_bp.route('/criterio_diagnostico_PorIdTranstorno/<int:id>', methods=['GET'])
def get_criterio_diagnostico_PorIdTranstorno(id):
    return jsonify(carregar_criterio_diagnostico_porIDTranstorno(id))

#criterio_diagnostico, criterio_diferencial, ID_TRANSTORNO
@criterio_diagnostico_bp.route('/criterio_diagnostico', methods = ['POST'])
def post_criterio_diagnostico():
    data = request.json
    try:
        return criar_criterio_diagnostico(
            criterio_diagnostico = data.get('criterio_diagnostico'),
            criterio_diferencial= data.get('criterio_diferencial'),
            cd_transtorno = data.get('cd_transtorno')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@criterio_diagnostico_bp.route('/criterio_diagnostico/<int:id>', methods=['PUT'])
def put_criterio_diagnostico(id):
    data = request.json
    return atualizar_criterio_diagnostico(id, **data)

@criterio_diagnostico_bp.route('/criterio_diagnostico/<int:id>', methods=['DELETE'])
def deletar_criterio_diagnostico_fim(id):
    return deletar_criterio_diagnostico(id)

@criterio_diagnostico_bp.route('/criterio_diagnostico/all/<int:id>', methods=['DELETE'])
def deletarTodos_criterio_diagnostico_fim(id):
    return deletarTodos_criterio_diagnostico(id)

@criterio_diagnostico_bp.route('/criterio_diagnostico/deletarPorTranstorno/<int:id>', methods=['DELETE'])
def deletar_criterioPorIdTranstorno_fim(id):
    return deletar_criterioPorIdTranstorno(id)