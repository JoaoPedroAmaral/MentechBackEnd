from flask import jsonify, request, Blueprint
from Controller.endereco import carregar_endereco, criar_endereco, atualizar_endereco, deletar_endereco, carregar_endereco_by_id

endereco_bp = Blueprint("endereco_bp", __name__)


@endereco_bp.route('/endereco', methods=['GET'])
def get_endereco():
    return jsonify(carregar_endereco())

@endereco_bp.route('/endereco/<int:cd_paciente>', methods=['GET'])
def get_endereco_por_paciente(cd_paciente):
    return jsonify(carregar_endereco_by_id(cd_paciente))


#ID_PACIENTE, ID_RESPONSAVEL, cidade, bairro, logradouro, NUM, cep, uf, complemento
@endereco_bp.route('/endereco', methods = ['POST'])
def post_endereco():
    data = request.json
    try:
        return criar_endereco(
            cd_paciente = data.get('cd_paciente'),
            tipo = data.get('tipo'),
            cd_responsavel = data.get('cd_responsavel'),
            cidade = data.get('cidade'),
            bairro = data.get('bairro'),
            logradouro = data.get('logradouro'),
            cep = data.get('cep'),
            uf = data.get('uf'),
            complemento= data.get('complemento'),
            numero = data.get('numero')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@endereco_bp.route('/endereco/<int:id>', methods=['PUT'])
def put_endereco(id):
    data = request.json
    return atualizar_endereco(id, **data)


@endereco_bp.route('/endereco/<int:id>', methods=['DELETE'])
def deletar_endereco_fim(id):
    return deletar_endereco(id)
