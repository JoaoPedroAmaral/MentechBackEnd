from flask import jsonify, request, Blueprint
from Controller.meta import carregar_meta, criar_meta, inativar_meta, carregar_meta_PorPaciente,remover_meta

meta_bp = Blueprint("meta_bp", __name__)


@meta_bp.route('/meta', methods=['GET'])
def get_meta():
    meta = carregar_meta()
    return jsonify(meta)

@meta_bp.route('/meta/por_paciente/<int:cd_paciente>', methods=['GET'])
def get_meta_poridpaciente(cd_paciente):
    meta = carregar_meta_PorPaciente(cd_paciente)
    return jsonify(meta)

@meta_bp.route('/meta', methods = ['POST'])
def post_meta():
    data = request.json
    try:
        return criar_meta(
            meta = data.get('meta'),
            obs_meta = data.get('obs_meta')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


"""@meta_bp.route('/meta/<int:id>', methods=['PUT'])
def put_meta(id):
    data = request.json
    update_meta(id, **data)
    return jsonify({"message": "meta atualizada com sucesso!"})"""

@meta_bp.route('/meta/<int:cd_meta>', methods=['DELETE'])
def deletar_meta_fim(cd_meta):
   return remover_meta(cd_meta)

@meta_bp.route('/meta/alternar/<int:id>', methods=['PUT'])
def put_inativar_meta(id):
    return inativar_meta(id)
    

