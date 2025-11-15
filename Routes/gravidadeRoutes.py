from flask import jsonify, request, Blueprint
from Controller.gravidade import deletar_gravidadePorIDTranstorno, carregar_gravidade, criar_gravidade, deletar_gravidade,atualizar_gravidade, deletarTodos_gravidade, carregar_gravidade_PorIdTranstorno

gravidade_bp = Blueprint("gravidade_bp", __name__)


@gravidade_bp.route('/gravidade', methods=['GET'])
def get_gravidade():
    gravidade = carregar_gravidade()
    return jsonify(gravidade)


@gravidade_bp.route('/gravidade_PorIdTranstorno/<int:id>', methods=['GET'])
def get_gravidade_PorIdTranstorno(id):
    gravidade = carregar_gravidade_PorIdTranstorno(id)
    return jsonify(gravidade)

#grav_descricao
@gravidade_bp.route('/gravidade', methods = ['POST'])
def post_gravidade():
    data = request.json
    try:
        return criar_gravidade(
            nm_gravidade = data.get('nm_gravidade'),
            grav_descricao = data.get('grav_descricao'),
            cd_transtorno= data.get('cd_transtorno'),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@gravidade_bp.route('/gravidade/<int:id>', methods=['PUT'])
def put_gravidade(id):
    data = request.json
    return atualizar_gravidade(id, **data)
    
@gravidade_bp.route('/gravidade/<int:id>', methods=['DELETE'])
def deletar_gravidade_fim(id):
    return deletar_gravidade(id)
    
@gravidade_bp.route('/gravidade/all/<int:id>', methods=['DELETE'])
def deletar_especificadorTodos_fim(id):
    return deletarTodos_gravidade(id)

@gravidade_bp.route('/gravidade/deletarPorTranstorno/<int:id>', methods=['DELETE'])
def deletar_gravidadePorID_fim(id):
    return deletar_gravidadePorIDTranstorno(id)