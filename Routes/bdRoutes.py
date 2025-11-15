from flask import jsonify, request, Blueprint
from Controller.log import definir_usuario
bd_bp = Blueprint("bd_bp", __name__)

@bd_bp.route('/definir_usuario/<int:CD_USUARIO_LOGADO>', methods = ['POST'])
def definir_usuario_post(CD_USUARIO_LOGADO):
    try:
        definir_usuario(CD_USUARIO_LOGADO)
        return jsonify({'Usuário Declarado': CD_USUARIO_LOGADO})
    except Exception as e:
        return jsonify({"error": str(e)}),400