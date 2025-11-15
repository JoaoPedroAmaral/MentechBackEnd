from flask import jsonify, Blueprint, request
from Controller.mensagens import carregar_mensagens, enviar_mensagem_positiva, enviar_mensagem_negativa
mensagem_bp = Blueprint("mensagem_bp", __name__)


@mensagem_bp.route('/mensagem', methods=['GET'])
def get_mensagem():
    mensagem = carregar_mensagens()
    return jsonify(mensagem)

@mensagem_bp.route('/mensagemPostitiva', methods=['GET'])
def get_mensagem_positiva():
    MSG = request.args.get('msg')  
    mensagem = enviar_mensagem_positiva(MSG)
    return jsonify(mensagem)

@mensagem_bp.route('/mensagemNegativa', methods=['GET'])
def get_mensagem_negativa():
    MSG = request.args.get('msg')  
    mensagem = enviar_mensagem_negativa(MSG)
    return jsonify(mensagem)