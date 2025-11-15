from flask import jsonify, request, Blueprint
from Controller.genero import deletar_genero, carregar_genero, cadastrar_genero, atualizar_genero
genero_bp = Blueprint("genero_bp", __name__)


@genero_bp.route('/genero', methods=['GET'])
def get_genero():
    genero = carregar_genero()
    return jsonify(genero)

@genero_bp.route('/genero', methods = ['POST'])
def post_genero():
    data = request.json
    try:
        return  cadastrar_genero(
            nm_genero = data.get('nm_genero'),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@genero_bp.route('/genero/<int:id>', methods=['PUT'])
def put_genero(id):
    data = request.json
    return atualizar_genero(id, **data)

@genero_bp.route('/genero/<int:id>', methods=['DELETE'])
def deletar_genero_fim(id):
    return deletar_genero(id)

