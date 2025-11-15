from flask import jsonify, request, Blueprint
from Controller.patologia import carregar_patologia, criar_patologia, deletar_patologia, atualizar_patologia, carregar_patologia_by_id

patologia_bp = Blueprint("patologia_bp", __name__)


@patologia_bp.route('/patologia', methods=['GET'])
def get_patologia():
    patologias = carregar_patologia()
    return jsonify(patologias)

@patologia_bp.route('/patologia/<int:id>', methods=['GET'])
def get_patologia_id(id):
    patologia = carregar_patologia_by_id(id)
    if patologia:
        return jsonify(patologia)
    elif patologia is None:
        return jsonify({"Warning": "Paciente sem patologia"}), 200
    else:
        return jsonify({"error": "Patologia não encontrada"}), 404

@patologia_bp.route('/patologia', methods = ['POST'])
def post_patologia():
    data = request.json
    print(data)
    try:
        return criar_patologia(
            cd_paciente=data.get('cd_paciente'),
            doenca = data.get('doenca'),
            obs_doenca = data.get('obs_doenca'),
            cid11 = data.get('cid11')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# @patologia_bp.route('/patologia/<int:id>', methods=['PUT'])
# def put_patologia(id):
#     data = request.json
#     atualizar_patologia(id, **data)
#     return jsonify({"message": "Patologia atualizada com sucesso!"})

@patologia_bp.route('/patologia/<int:id>', methods=['DELETE'])
def delete_patologia_fim(id):
    return deletar_patologia(id)
