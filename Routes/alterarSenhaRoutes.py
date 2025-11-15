from flask import jsonify, request, Blueprint
from Controller.alterar_senha import carregar_pedidos, criar_solicitacao, utilizar_token, carregar_pedidos_por_id_usuario,alterar_senha

alterar_senha_bp = Blueprint("alterar_senha_bp", __name__)


@alterar_senha_bp.route('/alterar_senha', methods=['GET'])
def get_alterar_senha():
    alterar_senhas = carregar_pedidos()
    return jsonify(alterar_senhas)

@alterar_senha_bp.route('/alterar_senha/<int:cd_usuario>', methods=['GET'])
def get_alterar_senha_por_usuario(cd_usuario):
    try:  
        alterar_senhas = carregar_pedidos_por_id_usuario(cd_usuario)
        if alterar_senhas:
            return jsonify(alterar_senhas)
        else:
            return jsonify({"error": "O usuário não possui solicitações"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#NM_alterar_senha, DESCRICAO_alterar_senha, DT_alterar_senha, parecer_tecnico, resultado, cd_meta
#Q porr é isso joao? kkkkkk
@alterar_senha_bp.route('/alterar_senha', methods=['POST'])
def post_alterar_senha():
    data = request.json
    try:
        return criar_solicitacao(
            cd_usuario=data.get('cd_usuario'),
            email_destino=data.get('email')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@alterar_senha_bp.route('/alterar_senha/<int:id>', methods=['PUT'])
def put_utilizar_token(id):
    data = request.json
    nova_senha = data.get("nova_senha")
    usuario_id = data.get("cd_usuario")

    # 1️⃣ Valida o token
    tokenValido = utilizar_token(id)
    if not tokenValido:
        return jsonify({"error": "Token inválido ou expirado"}), 400

    # 2️⃣ Altera a senha
    return alterar_senha(usuario_id, nova_senha)
