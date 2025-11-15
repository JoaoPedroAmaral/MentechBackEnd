from flask import jsonify, request, Blueprint
from Controller.subtipo_transtorno import carregar_subtipo_transtorno, criar_subtipo_transtorno, deletar_subtipo_transtorno, atualizar_subtipo_transtorno, carregar_subtipo_transtorno_PorIdTranstorno, deletar_subtipoPorIdTranstorno, carregar_subtipo_transtorno_PorIdSubtipo

subtipo_transtorno_bp = Blueprint("subtipo_transtorno_bp", __name__)


@subtipo_transtorno_bp.route('/subtipo_transtorno', methods=['GET'])
def get_subtipo():
    subtipo = carregar_subtipo_transtorno()
    return jsonify(subtipo)

@subtipo_transtorno_bp.route('/subtipo_transtorno_PorIdTranstorno/<int:id>', methods=['GET'])
def get_subtipo_PorIdTranstorno(id):
    subtipo = carregar_subtipo_transtorno_PorIdTranstorno(id)
    return jsonify(subtipo)

@subtipo_transtorno_bp.route('/subtipo_transtorno_PorIdSubtipo/<int:id>', methods=['GET'])
def get_subtipo_PorIdSubtipo(id):
    subtipo = carregar_subtipo_transtorno_PorIdSubtipo(id)
    return jsonify(subtipo)

#nm_subtipo, cid11, obs, cd_transtorno
@subtipo_transtorno_bp.route('/subtipo_transtorno', methods = ['POST'])
def post_subtipo():
    data = request.json
    try:
        return criar_subtipo_transtorno(
            nm_subtipo = data.get('nm_subtipo'),
            cid11 = data.get('cid11'),
            obs = data.get('obs'),
            cd_transtorno = data.get('cd_transtorno')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@subtipo_transtorno_bp.route('/subtipo_transtorno/<int:id>', methods=['PUT'])
def put_subtipo(id):
    data = request.json
    return atualizar_subtipo_transtorno(id, **data)

@subtipo_transtorno_bp.route('/subtipo_transtorno/<int:id>', methods=['DELETE'])
def delete_subtipo_fim(id):
    return deletar_subtipo_transtorno(id)

@subtipo_transtorno_bp.route('/subtipo_transtorno/deletarPorTranstorno/<int:id>', methods=['DELETE'])
def delete_subtipoPorIdTranstorno_fim(id):
    return deletar_subtipoPorIdTranstorno(id)