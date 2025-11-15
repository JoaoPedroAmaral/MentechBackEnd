from flask import jsonify, request, Blueprint
from Controller.responsavel import carregar_responsavel, criar_responsavel, atualizar_responsavel, deletar_responsavel, carregar_responsavel_by_id, deletar_responsavel_porID
from datetime import datetime, date

responsavel_bp = Blueprint("responsavel_bp", __name__)


@responsavel_bp.route('/responsavel', methods=['GET'])
def get_responsavel():
    metas = carregar_responsavel()
    return jsonify(metas)

@responsavel_bp.route('/responsavel/<int:cd_paciente>', methods=['GET'])
def get_responsavel_por_paciente(cd_paciente):
    try: 
        return carregar_responsavel_by_id(cd_paciente)
    except Exception as e: 
        return jsonify({"error": "Responsável não encontrado"}), 404
    

@responsavel_bp.route('/responsavel', methods = ['POST'])
def post_responsavel():
    data = request.json
    print(data)
    try:
       return criar_responsavel(
            cd_paciente = data.get('cd_paciente'),
            cpf = data.get('cpf'),
            nome = data.get('nome'),
            dt_nascimento = data.get('dt_nascimento')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@responsavel_bp.route('/responsavel/<int:id>', methods=['PUT'])
def put_responsavel(id):
    data = request.json
    return atualizar_responsavel(id, **data)

@responsavel_bp.route('/responsavel/paciente/<int:id>', methods=['DELETE'])
def delete_responsavel_byPacienteId_fim(id):
    return deletar_responsavel_porID(id)

@responsavel_bp.route('/responsavel/<int:id>', methods=['DELETE'])
def delete_responsavel_fim(id):
    return deletar_responsavel(id)
