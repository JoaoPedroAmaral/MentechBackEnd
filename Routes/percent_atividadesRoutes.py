from flask import jsonify, request, Blueprint
from Controller.percent_atividades import carregar_percent_atividades, historico_da_atividade, historico_atividades_meta

percent_atividade_bp = Blueprint("percent_atividade_bp", __name__)


@percent_atividade_bp.route('/percent_atividade', methods=['GET'])
def get_hst_atividade():
    percent_atividades = carregar_percent_atividades()
    return jsonify(percent_atividades)

@percent_atividade_bp.route('/percent_atividade/porAtividade/<int:cd_atividade>', methods=['GET'])
def get_historico_porAtividade(cd_atividade):
    hst_atividade = historico_da_atividade(cd_atividade)
    return jsonify(hst_atividade)

@percent_atividade_bp.route('/percent_atividade/porMeta/<int:cd_meta>', methods=['GET'])
def get_historico_porMeta(cd_meta):
    hst_atividade_meta = historico_atividades_meta(cd_meta)
    return jsonify(hst_atividade_meta)

