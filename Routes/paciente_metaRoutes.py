from flask import jsonify, request, Blueprint
from Controller.paciente_meta import concluir_meta, carregar_paciente_meta, criar_paciente_meta, deletar_paciente_meta,carregar_paciente_meta_por_id
from datetime import datetime

paciente_meta_bp = Blueprint("paciente_meta_bp", __name__)


@paciente_meta_bp.route('/paciente_meta', methods=['GET'])
def get_metas():
    paciente_meta = carregar_paciente_meta()
    return jsonify(paciente_meta)

@paciente_meta_bp.route('/paciente_meta/por_paciente/<int:cd_paciente>', methods=['GET'])
def get_metas_poridpaciente(cd_paciente):
    paciente_meta = carregar_paciente_meta_por_id(cd_paciente)
    return jsonify(paciente_meta)

@paciente_meta_bp.route('/paciente_meta', methods = ['POST'])
def post_metas():
    data = request.json
    print(data)
    try:
        return criar_paciente_meta(
            cd_meta = data.get('cd_meta'),
            cd_paciente = data.get('cd_paciente'),
            dt_previsao = data.get('dt_previsao')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


"""@paciente_meta_bp.route('/paciente_meta/<int:id>', methods=['PUT'])
def put_meta(id):
    data = request.json
    atualizar_meta(id, **data)
    return jsonify({"message": "relacao paciente_meta atualizada com sucesso!"})
"""

@paciente_meta_bp.route('/paciente_meta/<int:id>', methods=['DELETE'])
def deletar_paciente_meta_fim(id):
    return deletar_paciente_meta(id)

@paciente_meta_bp.route('/paciente_meta/<int:id>', methods=['PUT'])
def put_concluir_paciente_meta(id):
    return concluir_meta(id)
   