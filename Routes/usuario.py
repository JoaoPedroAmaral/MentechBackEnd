from flask import jsonify, request, Blueprint
from Controller.usuario import carregar_usuario, criar_usuario, atualizar_usuario, deletar_usuario

usuario_bp = Blueprint("usuario_bp", __name__)


@usuario_bp.route('/usuario', methods=['GET'])
def get_usuario():
    metas = carregar_usuario()
    return jsonify(metas)


@usuario_bp.route('/usuario', methods = ['POST'])
def post_usuario():
    data = request.json
    try:
        return criar_usuario(
            nm_usuario = data.get('nm_usuario'),
            senha = data.get('senha'),
            email = data.get('email'),
            cip = data.get('cip')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@usuario_bp.route('/usuario/<int:id>', methods=['PUT'])
def put_usuario(id):
    data = request.json
    return atualizar_usuario(id, **data)

@usuario_bp.route('/usuario/<int:id>', methods=['DELETE'])
def deletar_usuario_fim(id):
    return deletar_usuario(id)
