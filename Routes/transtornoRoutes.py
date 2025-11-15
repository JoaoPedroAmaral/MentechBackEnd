from flask import jsonify, request, Blueprint
from Controller.transtorno import carregar_transtorno, criar_transtorno, atualizar_transtorno, deletar_transtorno, carregar_transtorno_PorIdTranstorno



transtorno_bp = Blueprint("transtorno_bp", __name__)

@transtorno_bp.route('/transtorno', methods=['GET'])
def get_transtorno():
    transtorno = carregar_transtorno()
    return jsonify(transtorno)

@transtorno_bp.route('/transtorno_PorIdTranstorno/<int:id>', methods=['GET'])
def get_transtorno_PorIdTranstorno(id):
    transtorno = carregar_transtorno_PorIdTranstorno(id)
    return jsonify(transtorno)

@transtorno_bp.route('/transtorno', methods=['POST'])
def post_transtorno():
    data = request.json
    try:
        return criar_transtorno(
            nm_transtorno = data.get('nm_transtorno'),
            cid11 = data.get('cid11'),
            apoio_diag = data.get('apoio_diag'),
            prevalencia = data.get('prevalencia'),
            fatores_risco_prognostico = data.get('fatores_risco_prognostico'),
            diagnostico_genero = data.get('diagnostico_genero'),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@transtorno_bp.route('/transtorno/<int:id>', methods=['PUT'])
def put_transtorno(id):
    data = request.json
    return atualizar_transtorno(id, **data)

@transtorno_bp.route('/transtorno/<int:id>', methods=['DELETE'])
def delete_transtorno_fim(id):
    return deletar_transtorno(id)

@transtorno_bp.route('/transtorno')
def transtorno():
    return {"message": "Exemplo de resposta"}
