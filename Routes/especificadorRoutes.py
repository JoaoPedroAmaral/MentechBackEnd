from flask import jsonify, request, Blueprint
from Controller.especificador import carregar_especificador, criar_especicador, deletar_especificador,atualizar_especificador, deletarTodos_especificador

especificador_bp = Blueprint("especificador_bp", __name__)


@especificador_bp.route('/especificador', methods=['GET'])
def get_especificador():
    especificador = carregar_especificador()
    return jsonify(especificador)

#nome, DESCRICAO, ID_TRANSTORNO
@especificador_bp.route('/especificador', methods = ['POST'])
def post_especificador():
    data = request.json
    try:
        return criar_especicador(
            nome = data.get('NV_GRAVIDADE'),
            DESCRICAO = data.get('DESCRICAO'),
            ID_TRANSTORNO = data.get('ID_TRANSTORNO')
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@especificador_bp.route('/especificador/<int:id>', methods=['PUT'])
def put_especificador(id):
    data = request.json
    return atualizar_especificador(id, **data)
    
@especificador_bp.route('/especificador/<int:id>', methods=['DELETE'])
def delete_especificador_fim(id):
    return deletar_especificador(id)

@especificador_bp.route('/especificador/all/<int:id>', methods=['DELETE'])
def delete_especificadorTodos_fim(id):
    return deletarTodos_especificador(id)
    