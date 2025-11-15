from flask import jsonify, request, Blueprint
from Controller.telefone import carregar_telefone, criar_telefone, atualizar_telefone, deletar_telefone, carregar_telefone_por_id_paciente, carregar_telefone_por_id_responsavel

telefone_bp = Blueprint("telefone_bp", __name__)


@telefone_bp.route('/telefone', methods=['GET'])
def get_telefone():
    telefones = carregar_telefone()
    return jsonify(telefones)

@telefone_bp.route('/telefone/por_paciente/<int:cd_paciente>', methods=['GET'])
def get_telefone_por_paciente(cd_paciente):
    telefones = carregar_telefone_por_id_paciente(cd_paciente)
    return jsonify(telefones)

@telefone_bp.route('/telefone/por_responsavel/<int:cd_responsavel>', methods=['GET'])
def get_telefone_por_responsavel(cd_responsavel):
    telefones = carregar_telefone_por_id_responsavel(cd_responsavel)
    return jsonify(telefones)

@telefone_bp.route('/telefone', methods = ['POST'])
def post_telefone():
    data = request.json
    try:
        return criar_telefone(
            ddd = data.get('ddd'),
            nr_telefone = data.get('nr_telefone'),
            tipo = data.get('tipo'),
            cd_paciente = data.get('cd_paciente'),
            cd_responsavel = data.get('cd_responsavel')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@telefone_bp.route('/telefone/<int:id>', methods=['PUT'])
def put_telefone(id):
    data = request.json
    return atualizar_telefone(id, **data)

@telefone_bp.route('/telefone/<int:id>', methods=['DELETE'])
def delete_telefone_fim(id):
    return deletar_telefone(id)
